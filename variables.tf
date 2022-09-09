variable "api_token" {
  type        = string
  description = "the slack API token"
}

variable "slack_channels" {
  type        = string
  description = "The channel to send alerts to"
}

variable "filter_deploys" {
  type        = string
  description = "Do not send a notification for scaling activities related to deploys"
  default     = "true"
}

variable "filter_intermediate" {
  type        = string
  description = "Do not send notifications for pending, stopping, activating... containers."
}
