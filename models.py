import get_data
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import StratifiedKFold, GridSearchCV, RandomizedSearchCV, train_test_split


def models_main(model_type: str) -> None:
    df = get_data.combine_data()
    train, test = train_test_split(df, test_size=0.2, random_state=42)

    train = pd.get_dummies(train, columns=['Sex', 'Color', 'Breed'])
    test = pd.get_dummies(test, columns=['Sex', 'Color', 'Breed'])

    corr_matrix = train.corr()
    print('Correlation coefficients of survival from other features:\n',
          corr_matrix['Price'].sort_values(ascending=False)[1:])

    x_train = train.drop('Price', axis=1)

    y_train = train['Price']

    match model_type:
        case 'rfc':
            get_rfc_model(x_train, y_train)


def get_rfc_model(x_train: pd.DataFrame, y_train: pd.DataFrame) -> None:
    features = list(x_train)
    rfc = RandomForestRegressor(random_state=42)

    random_search_params = {'bootstrap': [True, False],
                            'criterion': ['squared_error', 'absolute_error', 'friedman_mse', 'poisson'],
                            'max_depth': list(np.arange(5, 25)),
                            'max_features': list(np.arange(1, len(features) + 1)),
                            'min_samples_leaf': list(np.arange(2, 6)),
                            'min_samples_split': list(np.arange(2, 11)),
                            'min_weight_fraction_leaf': list(np.arange(0.0, 0.4, 0.1)),
                            'n_estimators': list(np.arange(1, 200))}

    random_search = RandomizedSearchCV(rfc,
                                       param_distributions=random_search_params,
                                       n_iter=200,
                                       cv=StratifiedKFold(3),
                                       random_state=42)
    random_search.fit(x_train, y_train)

    random_search_parameters = pd.DataFrame(random_search.cv_results_).sort_values('rank_test_score').reset_index(
        drop=True)
    random_search_parameters = random_search_parameters.drop('params', axis=1)

    predictions = random_search.predict(x_train)
    random_search_rmse = np.sqrt(mean_squared_error(y_train, predictions))
    print('RMSE случайного поиска: ', random_search_rmse)

    top_models = random_search_parameters.head(3)
    param_bootstrap = [top_models['param_bootstrap'].value_counts().idxmax()]
    param_criterion = [top_models['param_criterion'].value_counts().idxmax()]
    param_max_depth = [x for x in set(top_models['param_max_depth'])]
    param_max_features = [x for x in set(top_models['param_max_features'])]
    param_min_samples_leaf = [x for x in set(top_models['param_min_samples_leaf'])]
    param_min_samples_split = [x for x in set(top_models['param_min_samples_split'])]
    param_min_weight_fraction_leaf = [x for x in set(top_models['param_min_weight_fraction_leaf'])]
    param_n_estimators = [x for x in set(top_models['param_n_estimators'])]

    params_grid = {'bootstrap': param_bootstrap,
                   'criterion': param_criterion,
                   'max_depth': param_max_depth,
                   'max_features': param_max_features,
                   'min_samples_leaf': param_min_samples_leaf,
                   'min_samples_split': param_min_samples_split,
                   'min_weight_fraction_leaf': param_min_weight_fraction_leaf,
                   'n_estimators': param_n_estimators}

    rfc = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(rfc, params_grid, cv=StratifiedKFold(3))
    grid_search.fit(x_train, y_train)
    best_parameters_model = grid_search.best_estimator_

    best_model = best_parameters_model
    best_model.fit(x_train, y_train)
    train_predictions = best_model.predict(x_train)
    grid_search_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
    print('Grid search best model RMSE: ', grid_search_rmse)
    print('The best hyperparameters for DecisionTreeRegressor found using grid search:\n',
          best_model.get_params())

    feature_importance = grid_search.best_estimator_.feature_importances_
    print('\nThe importance of each feature of model:',
          *sorted(zip(feature_importance, features), reverse=True), sep='\n')


models_main('rfc')
