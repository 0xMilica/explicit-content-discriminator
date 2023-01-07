import boto3
import urllib

rekognition = boto3.client('rekognition')
s3 = boto3.resource('s3')

def detect_moderation_labels(bucket, key):
    response = rekognition.detect_moderation_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

def set_default_image(bucket, key, default_image):
    copy_source = {
        'Bucket': bucket,
        'Key': default_image
    }
    s3.meta.client.copy(copy_source, bucket, key)

# --------------- Main handler ------------------
def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:
        response = detect_moderation_labels(bucket, key)
        for label in response["ModerationLabels"]:
            if label["ParentName"] == '' and label["Name"] == 'Explicit Nudity':
                if key.split('/')[0] == 'cover':
                    default_image = 'default_images/cover_prohibited.png'
                else: default_image = 'default_images/avatar_prohibited.png'

                set_default_image(bucket, key, default_image)
               
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e 
