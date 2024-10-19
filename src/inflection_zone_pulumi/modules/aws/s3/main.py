import pulumi_aws as aws

class s3:
    def __init__(self, values):
        self.s3_bucket = aws.s3.BucketV2(
            "s3-bucket",
            
            bucket = values.s3_properties["s3-bucket-name"]
        )

        self.s3_bucket_versioning = aws.s3.BucketVersioningV2(
            "s3-bucket-versioning",

            bucket = self.s3_bucket.id,

            versioning_configuration = {
                "status": values.s3_properties["s3-bucket-versioning"]
            }
        )