module "layer" {
  source       = "git::https://github.com/enter-at/terraform-aws-lambda-layer.git?ref=main"
  layer_name   = "dependencies"
  package_file = "./requirements.txt"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "src"
  output_path = ".terraform/src.zip"
}

resource "aws_lambda_function" "test_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = data.archive_file.lambda.output_path
  function_name = "lambda_function"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.9"

  layers = [
    module.layer.arn
  ]

  environment {
    variables = {
      foo = "bar"
    }
  }
}
