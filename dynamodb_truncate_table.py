import boto3
import argparse
dynamo = boto3.resource('dynamodb')

def truncateTable(tableName):
    table = dynamo.Table(tableName)
    
    #get the table keys
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    #Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#'+key: key for key in tableKeyNames}
    
    counter = 0
    page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            reply = str(input(f'{counter} will be deleted for table {tableName} (y/n): ')).lower().strip()
            if reply[:1] == 'y':
                # Delete items in batches
                for itemKeys in page["Items"]:
                    batch.delete_item(Key=itemKeys)
                # Fetch the next page
                if 'LastEvaluatedKey' in page:
                    page = table.scan(
                        ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                        ExclusiveStartKey=page['LastEvaluatedKey'])
                else:
                    break
            if reply[:1] == 'n':
                exit()
    print(f"Deleted {counter}")
            
parser = argparse.ArgumentParser(description='DynamoDB Drop all items in table.')
parser.add_argument('-t', '--table', help='The name of the table', required=True)
args = parser.parse_args()
truncateTable(args.table)
