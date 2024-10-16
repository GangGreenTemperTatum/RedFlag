import os
import requests
import json

from .console import (
    pretty_print,
    MessageType
)


class Slack():
    # The __init__ method initializes the Slack token and channel
    def __init__(
        self,
        token,
        channel
    ): 
        self.token = token
        self.channel = channel
        self.base_url = "https://slack.com/api/"
    
    # create function for each corresponding slack block kit element from oad_dict written in the main script
    def build_title_block(
        self,
        headline
    ) -> dict:
      return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": headline,
                "emoji": True
            }
        }

    def build_repo_info_block(
        self,
        repository,
        pr_title,
        commit_url=None
    ) -> dict:
        text = f"*Repository*: <https://github.com/{repository}|{repository}> \n"

        if commit_url:
            text += f"*Title*: <{commit_url}|{pr_title}>"

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }

    def build_reasoning_block_in_scope(
        self,
        reason_in_scope
    ) -> dict:
       return {
           "type": "section",
           "text":
               {
                "type": "mrkdwn",
                "text": f"*Model Review Reason:*\n\n{reason_in_scope}"
               }
       }

    def build_divider_block(self) -> dict:
       return {
            "type": "divider"
       }

    def build_slack_blocks(
        self,
        headline,
        results
    ) -> list:
        blocks = []
        in_scope = results["in_scope"]

        for obj in in_scope:
            if obj is None:
                continue

            # Extract the pr title nested object and append to the function blocks
            title_block = self.build_title_block(headline)
            blocks.append(title_block)

            # Extract the repo and url nested object and append to the function blocks
            pr_title  = obj.pr.title
            repository = obj.pr.repository
            commit_url = obj.pr.url
            info_block = self.build_repo_info_block(repository, pr_title, commit_url)
            blocks.append(info_block)

            # Extract the in_scope reason nested object and append to the function blocks
            reason_in_scope = obj.review.reasoning
            reason_in_scope_block = self.build_reasoning_block_in_scope(reason_in_scope)
            blocks.append(reason_in_scope_block)
#
        return blocks


    # The post_message method sends a message to the specified Slack channel using the Slack API
    def post_message(self, blocks):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }

        payload = {
            "channel": self.channel,
            "blocks": blocks
        }

        response = requests.post(
            url=f'{self.base_url}chat.postMessage',
            headers=headers,
            data=json.dumps(payload)
        )
    
        # Check if the response status code is not 200 (OK)
        if not response.status_code // 100 == 2:
            # Log the error or raise an exception
            raise Exception(f"Post Slack message failed: {response.status_code} - {response.text}")
        
        # If successful, pretty_print the success message
        pretty_print(
            f"Posted Slack message successfully in channel #{self.channel}",
            MessageType.INFO
        )
