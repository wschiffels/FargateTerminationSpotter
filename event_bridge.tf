/* eventbridge rule */
resource "aws_cloudwatch_event_rule" "termination" {
  name        = "TerminationSpotter"
  description = "Capture ECS/Fargate termination events"

  event_pattern = <<EOF
{
  "detail-type": [
    "ECS Task State Change"
  ],
  "source": [
    "aws.ecs"
  ]
}
EOF
}

/* target */
resource "aws_cloudwatch_event_target" "lamdba" {
  rule = aws_cloudwatch_event_rule.termination.name
  arn  = aws_lambda_function.spotter.arn
}
