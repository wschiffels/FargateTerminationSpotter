import json
import os
from unittest.mock import FILTER_DIR
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

slack_token = os.environ['SLACK_API_TOKEN']
slack_channel_id = os.environ['SLACK_CHANNEL_ID']
filter_deploys = os.environ["FILTER_DEPLOYS"]
filter_transitions = os.environ["FILTER_INTERMEDIATE"]
client = WebClient(token=slack_token)


def alert(event, context):

    def safeget(dct, *keys):
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return "n/a"
        return dct

    account = safeget(event, 'account')
    clusterArn = safeget(event, 'detail', 'clusterArn')
    cluster = clusterArn.split('/')[1]
    taskArn = safeget(event, 'detail', 'containers', 0, 'taskArn')
    lastStatus = safeget(event, 'detail', 'lastStatus')
    name = safeget(event, 'detail', 'containers', 0, 'name')
    desiredStatus = safeget(event, 'detail', 'desiredStatus')
    createdAt = safeget(event, 'detail', 'createdAt')
    startedAt = safeget(event, 'detail', 'startedAt')
    stoppedAt = safeget(event, 'detail', 'stoppedAt')
    stoppedReason = safeget(event, 'detail', 'stoppedReason')
    stopCode = safeget(event, 'detail', 'stopCode')

    # try format zulu time
    try:
        startedAt_obj = datetime.strptime(startedAt, '%Y-%m-%dT%H:%M:%S.%fZ')
        startedAt = startedAt_obj.strftime("%d.%m. %H:%M:%S UTC")
    except (ValueError, AttributeError):
        pass
    try:
        stoppedAt_obj = datetime. strptime(stoppedAt, '%Y-%m-%dT%H:%M:%S.%fZ')
        stoppedAt = stoppedAt_obj.strftime("%d.%m. %H:%M:%S UTC")
    except (ValueError, AttributeError):
        pass

    # don't notify for scheduled tasks
    if name == 'thanos_compactor':
        print('not reporting on scheduled task thanos_compactor.')
        return

    if (filter_deploys == 'true' and stopCode == "ServiceSchedulerInitiated"):
        print('not reporting on scheduled deploys')
        return

    if (filter_transitions == 'true'):
        if lastStatus in ('PENDING', 'ACTIVATING', 'PROVISIONING', 'DEPROVISIONING', 'DEACTIVATING'):
            print('not reporting transition states')
            return

    if lastStatus == "STOPPING":
        color = "#bf616a"
        msg = 'Task State Change: ' + name + " => *STOPPING*"
    elif lastStatus == "STOPPED":
        color = "#bf616a"
        msg = 'Task State Change: ' + name + " => *STOPPED*"
    elif lastStatus == "RUNNING":
        color = "#a3be8c"
        msg = 'Task State Change: ' + name + " => *RUNNING*"
    elif lastStatus == "PENDING":
        color = "#ebcb8b"
        msg = 'Task State Change: ' + name + " => *PENDING*"
    elif lastStatus == "ACTIVATING":
        color = "#ebcb8b"
        msg = 'Task State Change: ' + name + " => *ACTIVATING*"
    elif lastStatus == "PROVISIONING":
        color = "#ebcb8b"
        msg = 'Task State Change: ' + name + " => *PROVISIONING*"
    elif lastStatus == "DEPROVISIONING":
        color = "#bf616a"
        msg = 'Task State Change: ' + name + " => *DEPROVISIONING*"
    elif lastStatus == "DEACTIVATING":
        color = "#bf616a"
        msg = 'Task State Change: ' + name + " => *DEACTIVATING*"
    else:
        print("warum")
        color = "#d8dee9"
        msg = 'Task State Change: ' + name + " => " + lastStatus

    response = client.chat_postMessage(
        channel=slack_channel_id,
        text=msg,
        attachments=[
            {
                "color": color,
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Cluster:*\n" + cluster
                                },
                            {
                                    "type": "mrkdwn",
                                    "text": "*Task:*\n" + name
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Last Status:*\n" + lastStatus
                                },
                            {
                                    "type": "mrkdwn",
                                    "text": "*Desired Status:*\n" + desiredStatus
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Started:*\n" + startedAt
                                },
                            {
                                    "type": "mrkdwn",
                                    "text": "*Stopped:*\n" + stoppedAt
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Reason:*\n" + stoppedReason
                                },
                            {
                                    "type": "mrkdwn",
                                    "text": "*stopCode:*\n" + stopCode
                            }
                        ]
                    },
                ]
            }
        ]
    )

    return {}
