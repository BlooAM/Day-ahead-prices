import pandas as pd
import joblib
import json
from fastapi import FastAPI, Form, Request
import uvicorn

MODEL_DIR = "resources/"
FASTAPI_API = FastAPI()


def get_model(model_name='default'):
    model = joblib.load(MODEL_DIR + model_name)
    return model


def str_to_float_list(args):
    args = args.split(",")
    args = [float(arg) for arg in args]
    return args


model = get_model()

def get_params_postman(query_params):
    sep_length = str_to_float_list(query_params["sepLen"])
    sep_width = str_to_float_list(query_params["sepWid"])
    pet_length = str_to_float_list(query_params["petLen"])
    pet_width = str_to_float_list(query_params["petWid"])
    return (sep_length, sep_width, pet_length, pet_width)


@FASTAPI_API.post("/predict_price_postman")
def predict_price_postman(request: Request):
    query_params = dict(request.query_params)
    (sep_length, sep_width, pet_length, pet_width) = get_params_postman(query_params)
    new_obs = pd.DataFrame(
        {
            "sepal length (cm)": [float(x) for x in sep_length],
            "sepal width (cm)": [float(x) for x in sep_width],
            "petal length (cm)": [float(x) for x in pet_length],
            "petal width (cm)": [float(x) for x in pet_width],
        }
    )
    y_pred = list(model.predict(new_obs))
    y_pred = [str(x) for x in y_pred]
    response = {"y_pred": ",".join(y_pred)}
    return response


#%%CURL
def get_params_curls(input_var):
    sep_length = str_to_float_list(input_var["sepLen"])
    sep_width = str_to_float_list(input_var["sepWid"])
    pet_length = str_to_float_list(input_var["petLen"])
    pet_width = str_to_float_list(input_var["petWid"])
    return (sep_length, sep_width, pet_length, pet_width)


@FASTAPI_API.post("/predict_class_curl")
def predict_class_curl(input: str = Form(...)):
    input_var = eval(input)
    (sep_length, sep_width, pet_length, pet_width) = get_params_curls(input_var)
    new_obs = pd.DataFrame(
        {
            "sepal length (cm)": [float(x) for x in sep_length],
            "sepal width (cm)": [float(x) for x in sep_width],
            "petal length (cm)": [float(x) for x in pet_length],
            "petal width (cm)": [float(x) for x in pet_width],
        }
    )
    y_pred = list(model.predict(new_obs))
    y_pred = [str(x) for x in y_pred]
    response = {"y_pred": ",".join(y_pred)}
    return response


#%%
if __name__ == "__main__":
    uvicorn.run(FASTAPI_API, host="0.0.0.0", port=8080)