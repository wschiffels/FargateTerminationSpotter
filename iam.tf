/* role */
resource "aws_iam_role" "spotter" {
  name = "terminationspotter-iam-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

/* policy */
data "aws_iam_policy_document" "terminationspotter" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:CreateLogGroup",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.spotter.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "terminationspotter" {
  name        = "terminationspotter-iam-policy"
  path        = "/"
  description = "terminationspotter policy"
  policy      = data.aws_iam_policy_document.terminationspotter.json
}

/* policy attachment */
resource "aws_iam_role_policy_attachment" "terminationspotter" {
  role       = aws_iam_role.spotter.id
  policy_arn = aws_iam_policy.terminationspotter.arn
}
