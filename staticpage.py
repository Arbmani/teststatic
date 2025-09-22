import json
from typing import Optional, TypedDict

import pulumi
from pulumi import ResourceOptions
from pulumi_aws import s3
from html_helper import get_template

class StaticPageArgs(TypedDict, total=False):
    index_content: pulumi.Input[str]
    """The HTML content for index.html."""

    template_name: str

class StaticPage(pulumi.ComponentResource):
    endpoint: pulumi.Output[str]
    """The URL of the static website."""

    def __init__(self,
                 name: str,
                 args: StaticPageArgs,
                 opts: Optional[ResourceOptions] = None) -> None:

        super().__init__('static-page-component:index:StaticPage', name, {}, opts)

        content_input: pulumi.Input[str] = (
            args["index_content"]
            if "index_content" in args and args["index_content"] is not None
            else get_template(args.get("template_name", "a"))
        )


        # Create a bucket
        bucket = s3.Bucket(
            f'{name}-bucket',
            opts=ResourceOptions(parent=self))

        # Configure the bucket website
        bucket_website = s3.BucketWebsiteConfiguration(
            f'{name}-website',
            bucket=bucket.bucket,
            index_document={"suffix": "index.html"},
            opts=ResourceOptions(parent=bucket))

        # Create a bucket object for the index document
        s3.BucketObject(
            f'{name}-index-object',
            bucket=bucket.bucket,
            key='index.html',
            content=args.get("index_content"),
            content_type='text/html',
            opts=ResourceOptions(parent=bucket))

        # Create a public access block for the bucket
        bucket_public_access_block = s3.BucketPublicAccessBlock(
            f'{name}-public-access-block',
            bucket=bucket.id,
            block_public_acls=False,
            opts=ResourceOptions(parent=bucket))

        # Set the access policy for the bucket so all objects are readable.
        s3.BucketPolicy(
            f'{name}-bucket-policy',
            bucket=bucket.bucket,
            policy=bucket.bucket.apply(_allow_getobject_policy),
            opts=ResourceOptions(parent=bucket, depends_on=[bucket_public_access_block]))

        self.endpoint = bucket_website.website_endpoint

        # By registering the outputs on which the component depends, we ensure
        # that the Pulumi CLI will wait for all the outputs to be created before
        # considering the component itself to have been created.
        self.register_outputs({
            'endpoint': bucket_website.website_endpoint
        })


def _allow_getobject_policy(bucket_name: str) -> str:
    return json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:GetObject'],
                'Resource': [
                    f'arn:aws:s3:::{bucket_name}/*',  # policy refers to bucket name explicitly
                ],
            },
        ],
    })