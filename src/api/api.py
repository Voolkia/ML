import pickle
import random as rnd

import pandas as pd
from flask import Flask
from flask import render_template, render_template_string
from flask_restful import reqparse, Api, Resource

from helpers import args_to_pandas
from model import load_columns, load_model, feature_transformation
from configs import FILE_EXAMPLE_DS, FILE_COLUMNS, FILE_MODEL
from interpretation import get_feature_contributions
from utils import rows_to_urls, load_sample_dataset

"""
Werbservice interface for ML projects

Usage example:
  Run service with:
    python app.py

  On browser paste:
    http://localhost:5000/predictions?feature1=1&feature2=2&feature3=1&feature4=2&feature5=1&feature6=2&feature7=1&feature8=2&feature9=1&feature10=2

Return (dictionary):
  {
    Prediction: n(int[0,1])
    impact: {
      [feature_name : feature_importance(float[0,1])],
    }
  }

"""

application = Flask(__name__)
api = Api(application)
# load model
model = load_model(FILE_MODEL)
# load required columns
columns = load_columns(FILE_COLUMNS)


class Predict(Resource):
    parser = reqparse.RequestParser()
    # All the received features must be float
    for col in columns:
        parser.add_argument(f'{col}',
                            # type=float,
                            required=True,
                            help=f'{col} is required & should be numeric.')

    def get(self):
        features = self.parser.parse_args()

        # control all required features are passed.

        # create pandas dataframe
        row = args_to_pandas(features)
        # drop useless features (ids)
        # to_drop = []
        df = row[columns]
        # clean & transform dataset
        df = feature_transformation(df)
        # make positive (fraud) probability prediction
        prediction = model.predict_proba(df)[0, -1]
        # get feature contributions (force to 1 row)
        contributions = get_feature_contributions(model, df)
        # return json
        return {
            "Prediction": prediction,
            "Impact": contributions,
          }, 200


@application.route('/')
def testSamples():
    # load dataset
    df_sample = load_sample_dataset(FILE_EXAMPLE_DS)
    # creating list of urls
    urls = rows_to_urls(df_sample, 20)
    return '<br>'.join(urls)


# Setup the Api resource routing here
RESOURCES = [
  (Predict, '/predictions'),
]

for resource, endpoint in RESOURCES:
    api.add_resource(resource, endpoint)


if __name__ == '__main__':
    application.run(debug=True)
