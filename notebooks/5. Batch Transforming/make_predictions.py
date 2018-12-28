from config import PATH_DATASET, PATH_MODELO, PATH_PREDICCIONES
import pickle
import pandas as pd

if __name__ == "__main__":
    # LOADING DATASET
    dataset = pd.read_feather(PATH_DATASET)
    dataset = dataset.fillna(-999)

    # LODAING MODEL
    with open(PATH_MODELO, 'rb') as file:
        model = pickle.load(file)

    results = pd.DataFrame(dataset["CIF_ID"])
    dataset = dataset.drop(["CIF_ID"], axis=1)
    predictions = model.predict_proba(dataset)

    results[['PROB_NO_BAJA',
             'PROB_BAJA_1M',
             'PROB_BAJA_2M',
             'PROB_BAJA_3M']] = pd.DataFrame(predictions)
    breakpoint()
    # SAVING RESULTS
    results.to_csv(PATH_PREDICCIONES)
