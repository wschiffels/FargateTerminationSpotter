/* build lambda */
resource "null_resource" "lambda_build" {
  provisioner "local-exec" {
    command = <<-CMD
        cd lambda
        [ -d "package" ] && rm -rf package
        mkdir package
        cp setup.cfg package
        cp handler.py package
        pip3 install slack-sdk --target package/
CMD

    interpreter = ["sh", "-c"]
  }
}

data "archive_file" "lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/package/"
  output_path = "${path.module}/function.zip"

  depends_on = [
    null_resource.lambda_build
  ]
}

/* the lambda function */
resource "aws_lambda_function" "spotter" {
  filename         = "${path.module}/function.zip"
  function_name    = "termination-spotter"
  role             = aws_iam_role.spotter.arn
  handler          = "handler.alert"
  source_code_hash = data.archive_file.lambda_function.output_base64sha256
  runtime          = "python3.7"

  environment {
    variables = {
      SLACK_API_TOKEN     = var.api_token
      SLACK_CHANNEL_ID    = var.slack_channels
      FILTER_DEPLOYS      = var.filter_deploys
      FILTER_INTERMEDIATE = var.filter_intermediate
    }
  }

  depends_on = [
    null_resource.lambda_build
  ]
}

/* cloudwatch group */
resource "aws_cloudwatch_log_group" "spotter" {
  name = "/aws/lambda/termination-spotter"
}


resource "aws_lambda_permission" "eventbridge_to_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.spotter.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.termination.arn
}
