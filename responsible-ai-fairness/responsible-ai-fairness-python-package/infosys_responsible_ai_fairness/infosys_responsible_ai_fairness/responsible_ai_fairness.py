import numpy as np
import pandas as pd
import datetime
import logging
from logging import warning
from aif360.datasets import BinaryLabelDataset
from aif360.datasets import StandardDataset
from aif360.metrics import BinaryLabelDatasetMetric
from holisticai.bias.metrics import *
from holisticai.bias.mitigation import CalibratedEqualizedOdds
from holisticai.bias.mitigation import CorrelationRemover
from holisticai.bias.mitigation import EqualizedOdds
from holisticai.bias.mitigation import LPDebiaserBinary
from holisticai.bias.mitigation import LearningFairRepresentation
from holisticai.bias.mitigation import MLDebiaser
from holisticai.bias.mitigation import RejectOptionClassification
from holisticai.bias.mitigation import Reweighing
from holisticai.bias.mitigation import preprocessing
from holisticai.pipeline import Pipeline
from sklearn import metrics
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.preprocessing import StandardScaler
from aif360.algorithms.preprocessing.disparate_impact_remover import DisparateImpactRemover as DIR
from aif360.algorithms.preprocessing.reweighing import Reweighing as RW
from aif360.datasets import BinaryLabelDataset

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


privileged_groups = [{}]
unprivileged_groups = [{}]
datalist = {}


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ProtetedAttribute:
    def __init__(self, name, privileged, unprivileged):
        self.protetedAttribute = {"name": name, "privileged": privileged, "unprivileged": unprivileged}
        self.protetedAttribute = AttributeDict(self.protetedAttribute)


class BiasResults:
    def __init__(self, Biased, protectedcAttrib, metrics):
        self.biasResults = {"biasDetected": Biased, "protectedAttribute": protectedcAttrib, "metrics": metrics}
        self.biasResults = AttributeDict(self.biasResults)


class metricsEntity:
    def __init__(self, name, description, value):
        self.metricsEntity = {"name": name, "description": description, "value": value}
        self.metricsEntity = AttributeDict(self.metricsEntity)


class MitigationResults:
    def __init__(self, biasType, mitigation_type, mitigation_technique, original_score_value_list,
                 original_bias_detected,
                 score_value_list, bias_detected,fileName):
        self.mitigationResults = {"biasType": biasType, "mitigationType": mitigation_type,
                                  "mitigationTechnique": mitigation_technique,
                                  "metricsBeforeMitigation": original_score_value_list,
                                  "biasDetectedOriginally": original_bias_detected,
                                  "metricsAfterMitigation": score_value_list,
                                  "biasDetectedAfterMitigation": bias_detected,
                                  "mitigatedFileName":fileName
                                  }
        self.mitigationResults = AttributeDict(self.mitigationResults)
        
    #dataset class for individual fairness
class StandardDataset(BinaryLabelDataset):
    def __init__(self, df, label_name, favorable_classes,
                 protected_attribute_names, privileged_classes,
                 instance_weights_name='', scores_name='',
                 categorical_features=[], features_to_keep=[],
                 features_to_drop=[], na_values=[], custom_preprocessing=None,
                 metadata=None):
        
        # 2. Perform dataset-specific preprocessing
        if custom_preprocessing:
            df = custom_preprocessing(df)

        # 3. Drop unrequested columns
        features_to_keep = features_to_keep or df.columns.tolist()
        keep = (set(features_to_keep) | set(protected_attribute_names)
              | set(categorical_features) | set([label_name]))
        if instance_weights_name:
            keep |= set([instance_weights_name])
        df = df[sorted(keep - set(features_to_drop), key=df.columns.get_loc)]
        categorical_features = sorted(set(categorical_features) - set(features_to_drop), key=df.columns.get_loc)

        # 4. Remove any rows that have missing data.
        dropped = df.dropna()
        count = df.shape[0] - dropped.shape[0]
        if count > 0:
            warning("Missing Data: {} rows removed from {}.".format(count,
                    type(self).__name__))
        df = dropped

        # 5. Create a one-hot encoding of the categorical variables.
        df = pd.get_dummies(df, columns=categorical_features, prefix_sep='=')
        
       #removed the code related to protected attributes

        # 7. Make labels binary
        favorable_label = 1.
        unfavorable_label = 0.
        if callable(favorable_classes):
            df[label_name] = df[label_name].apply(favorable_classes)
        elif np.issubdtype(df[label_name], np.number) and len(set(df[label_name])) == 2:
            # labels are already binary; don't change them
            favorable_label = favorable_classes[0]
            unfavorable_label = set(df[label_name]).difference(favorable_classes).pop()
        else:
            # find all instances which match any of the favorable classes
            pos = np.logical_or.reduce(np.equal.outer(favorable_classes, 
                                                      df[label_name].to_numpy()))
            df.loc[pos, label_name] = favorable_label
            df.loc[~pos, label_name] = unfavorable_label

        super(StandardDataset, self).__init__(df=df, label_names=[label_name],
            protected_attribute_names=protected_attribute_names,
            privileged_protected_attributes=[],
            unprivileged_protected_attributes=[],
            instance_weights_name=instance_weights_name,
            scores_names=[scores_name] if scores_name else [],
            favorable_label=favorable_label,
            unfavorable_label=unfavorable_label, metadata=metadata)        
        
class utils:
    FILE_NAME=""
    def get_mitigated_data(self,train,original_data,postProcessing):
        #get name of columns which are not in mitigated data
        additional_columns=[col for col in original_data.columns if col not in train.columns]
        #preprocess original data
        for col in original_data:
            original_data.loc[original_data[col] == "?", col] = np.nan     
        df_ = original_data.copy()
        #dropping columns where sum of missing values is greater than 1000
        df_clean = df_.iloc[:, [i for i, n in enumerate(df_.isna().sum(axis=0).T.values) if n < 1000]]
        df_clean_ = df_clean.dropna(axis=0,how="any")
        df_clean_=df_clean_.reset_index(drop=True)
        #merge both mitigated data and original_data
        df3=train.merge(df_clean_,suffixes=('_left', '__right__'), left_index=True, right_index=True)
        #drop columns which are already present in df as mitigated column
        df3.drop(list(df3.filter(regex='__right__')), axis=1, inplace=True)
        column_dict={}
        df_columns=df3.columns.values.tolist()
        #remove _left from column names
        df_columns=[s for s in df_columns if "_left" in s]
        for i in df_columns:            
            slice_obj = slice(-5)
            key=i
            value=i[slice_obj]
            column_dict[key]=value
        df3.rename(columns=column_dict,inplace=True)
        #move labels_pred to end of dataframe
        if(postProcessing):
            df3["labels_pred"]=df3.pop("labels_pred")
        return df3
    
    #for individual fairness
    def consistency(self,dataset,n_neighbors=5):
        X = dataset.features
        num_samples = X.shape[0]
        y = dataset.labels

        # learn a KNN on the features
        nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree')
        nbrs.fit(X)
        _, indices = nbrs.kneighbors(X)

        # compute consistency score
        consistency = 0.0
        for i in range(num_samples):
            consistency += np.abs(y[i] - np.mean(y[indices[i]]))
        consistency = 1.0 - consistency/num_samples

        return consistency
    
    

class DataList:
    def createdataset(self, df, label_name, favourableOutcome, protectedAttributes, CategoricalAttributes,features):
        protected_attribute = list(protectedAttributes.name)
        privilegedvar = protectedAttributes.privileged
        instance_weight=""
        if "instance weights" in features:
            instance_weight="instance weights"
        else:
            instance_weight=''
        dataset_orig = StandardDatasetDup(df=df, label_name=label_name, favorable_classes=favourableOutcome,
                                       protected_attribute_names=protected_attribute,
                                       privileged_classes=privilegedvar,
                                       instance_weights_name=instance_weight,
                                       categorical_features=CategoricalAttributes,
                                       features_to_keep=[], features_to_drop=[],
                                       na_values=[], custom_preprocessing=None,
                                       metadata={}
                                       )
        return dataset_orig

    def getDataList(self, datasetPath, labelmap, label, protectedAttributes, favourableOutcome,
                    CategoricalAttributes, features, biastype,flag) -> list:
        protected_attribute = protectedAttributes.name
        privileged_groups[0] = {}
        unprivileged_groups[0] = {}
        for i in range(len(protected_attribute)):
            privileged_groups[0][protected_attribute[i]] = 1.0
            unprivileged_groups[0][protected_attribute[i]] = 0.0
        features.append(label)
        ds = DataList()
        if (biastype == "PRETRAIN"):
            if flag == False:
                df = pd.read_csv(datasetPath, sep=",", usecols=features)
                dataset_orig = ds.createdataset(df, label, favourableOutcome, protectedAttributes,
                                            CategoricalAttributes,features)
            else:
                dataset_orig = ds.createdataset(datasetPath, label, favourableOutcome, protectedAttributes,
                                            CategoricalAttributes,features)
            datalist['dataset_original'] = dataset_orig
        return datalist

    def feature_selection(self, df, feature_list, label):
        dict_corr = {}
        for each in list(df.columns):
            corr = df[label].corr(df[each])
            dict_corr[each] = corr
        updated_dict_corr = {k: v for k, v in sorted(dict_corr.items(), key=lambda item: item[1], reverse=True)}
        new_dict = {}
        for key in list(updated_dict_corr.keys()):
            if key in feature_list:
                new_dict[key] = updated_dict_corr[key]
        columns = [k for k, v in new_dict.items() if v > 0 and v != 1]
        selected_columns = columns + [label]
        return df[selected_columns]

    def target_column_return(self, df, test_flag=False):
        if test_flag:
            if "labels_pred" in list(df.columns):
                df = df.drop(["labels_pred"], axis=1)
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        return X, y

    def preprocessDataset(self, df, label, label_map, protectedAttributes, taskType,flag,predLabel="labels_pred"):
        if flag==False:
            df = pd.read_csv(df, sep=",")
        df_orig = df.copy()
        if predLabel in list(df.columns):
            df = df.drop([predLabel], axis=1)
        feature_list = list(df.columns)
        pa_name = protectedAttributes.name[0]
        privileged = protectedAttributes.privileged[0]
        unprivileged = protectedAttributes.unprivileged[0]
        ds = DataList()

        # Convert "?" elements to NaN elements; from dataframe
        for col in df:
            df.loc[df[col] == "?", col] = np.nan
        # Remove NaN elements from dataframe
        df_ = df.copy()
        df_clean = df_.iloc[:, [i for i, n in enumerate(df_.isna().sum(axis=0).T.values) if n < 1000]]
        df_clean = df_clean.dropna()
        # Get the protected attribute vectors
        group_unprivileged = df_clean[pa_name].isin(unprivileged)
        group_privileged = df_clean[pa_name].isin(privileged)

        group_unprivileged = np.squeeze(group_unprivileged.values)
        group_privileged = np.squeeze(group_privileged.values)
        # Remove unnecessary columns
        df_clean[label].replace(label_map, inplace=True)

        tmp = pd.get_dummies(df_clean.drop(columns=[label, pa_name]))
        df_clean = pd.concat([tmp, df_clean[label].astype("uint8")], axis=1)
        df_clean = ds.feature_selection(df_clean, feature_list, label)
        if predLabel in list(df_orig.columns):
            df_clean[predLabel] = df_orig[predLabel]
        df_clean.rename(columns={label: "label"}, inplace=True)
        return group_unprivileged, group_privileged, df_clean, df_orig


class BiasResult:
    def mitigateAndTransform(self,datalist,protectedAttributes,mitigationTechnique):
        if mitigationTechnique == "DISPARATE IMPACT REMOVER":
            obj = DIR(repair_level=1.0)
            dataset_transf_train = obj.fit_transform(datalist['dataset_original'])
            column_names = dataset_transf_train.feature_names
            trans_df = pd.DataFrame(dataset_transf_train.features, columns=column_names)
            label_nm = dataset_transf_train.label_names
            trans_df[label_nm] = dataset_transf_train.labels
            transformedfile=trans_df
        elif mitigationTechnique == "REWEIGHING":
            obj = RW(unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)
            dataset_transf_train = obj.fit_transform(datalist['dataset_original'])
            column_names=dataset_transf_train.feature_names
            trans_df=pd.DataFrame(dataset_transf_train.features,columns=column_names)
            label_nm = dataset_transf_train.label_names
            trans_df[label_nm] = dataset_transf_train.labels
            trans_df["instance weights"]=dataset_transf_train.instance_weights
            transformedfile=trans_df
        return transformedfile
        	
    def analyzeResult(self, biastype, methods, protectedAttributes, datalist):
        protected_list = []
        for i in range(len(protectedAttributes.name)):
            obj_protectAttrib = ProtetedAttribute(name=protectedAttributes.name[i],
                                                  privileged=protectedAttributes.privileged[i],
                                                  unprivileged=protectedAttributes.unprivileged[i])
            protected_list.append(obj_protectAttrib.protetedAttribute)
        list_metric_results = []
        biased = False
        biased_list = []
        for i in range(len(methoddict[biastype][methods])):
            List_metric_score = methoddict[biastype][methods][i](datalist)
            if methods == "DISPARATE-IMPACT":
                if List_metric_score["value"] != 1.0:
                    biased = True
                else:
                    biased = False
            else:
                if List_metric_score["value"] != 0.0:
                    biased = True
                else:
                    biased = False
            List_metric_score["value"] = str(List_metric_score["value"])
            biased_list.append(biased)
            list_metric_results.append(List_metric_score)

        if True in biased_list:
            biased = True
        else:
            biased = False

        bias_list = []
        obj_biasresults = BiasResults(Biased=biased,
                                      protectedcAttrib=protected_list,
                                      metrics=list_metric_results)
        bias_list.append(obj_biasresults.biasResults)

        return (bias_list)
    
    def analyseHoilisticAIBiasResult(self, taskType, methods, group_unprivileged, group_privileged, predicted_y,
                                     actual_y, protectedAttributes):

        protected_list = []
        for i in range(len(protectedAttributes.name)):
            obj_protectAttrib = ProtetedAttribute(name=protectedAttributes.name[i],
                                                  privileged=protectedAttributes.privileged[i],
                                                  unprivileged=protectedAttributes.unprivileged[i])
            protected_list.append(obj_protectAttrib.protetedAttribute)

        if taskType == "CLASSIFICATION":
            taskType = "BINARY CLASSIFICATION"

        ref_vals = {
            "BINARY CLASSIFICATION": {"STATISTICAL_PARITY": 0,
                                      "DISPARATE_IMPACT": 1,
                                      "FOUR_FIFTHS_RULE": 1,
                                      "COHEN_D": 0,
                                      "EQUAL_OPPORTUNITY_DIFFERENCE": 0,
                                      "FALSE_POSITIVE_RATE_DIFFERENCE": 0,
                                      "FALSE_NEGATIVE_RATE_DIFFERENCE": 0,
                                      "TRUE_NEGATIVE_RATE_DIFFERENCE": 0,
                                      "AVERAGE_ODDS_DIFFERENCE": 0,
                                      "ACCURACY_DIFFERENCE": 0,
                                      "ABROCA": 0,
                                      "2SD Rule": 0,
                                      "Z_TEST_RATIO":0,
                                      "Z_TEST_DIFFERENCE":0},
            "REGRESSION": {"AVERAGE SCORE DIFFERENCE": 0,
                           "CORRELATION DIFFERENCE": 0,
                           "DISPARATE IMPACT QUANTILE": 1,
                           "MAE RATIO": 1,
                           "MAX STATISTICAL PARITY": 0,
                           "RMSE": 1,
                           "STATISTICAL PARITY AUC": 0,
                           "STATISTICAL PARITY QUANTILE": 0,
                           "ZSCORE DIFFERENCE": 0},
            "CLUSTERING": {"CLUSTER BALANCE": 1,
                           "CLUSTER DISTRIBUTION KL": 0,
                           "CLUSTER DISTRIBUTION TOTAL VARIATION": 0,
                           "MINIMUM CLUSTER RATIO": 1}
        }

        list_metric_results = []
        biased = False
        biased_list = []
        if methods!="ALL":
            List_metric_score = holisticaiMetrics[taskType][methods](group_unprivileged, group_privileged,predicted_y, actual_y)
            if (methods in list(ref_vals[taskType].keys())):
                log.info("method name: " + methods)
                if List_metric_score["value"] != ref_vals[taskType][methods]:
                    biased = True
                else:
                    biased = False    
            List_metric_score["value"] = str(List_metric_score["value"])
            biased_list.append(biased)
            list_metric_results.append(List_metric_score)  
        else:
            methodList=[]
            if taskType == "BINARY CLASSIFICATION":
                methodList = ["STATISTICAL_PARITY", "DISPARATE_IMPACT", "FOUR_FIFTHS_RULE", "COHEN_D", "EQUAL_OPPORTUNITY_DIFFERENCE",
                                    "FALSE_POSITIVE_RATE_DIFFERENCE", "FALSE_NEGATIVE_RATE_DIFFERENCE","TRUE_NEGATIVE_RATE_DIFFERENCE","AVERAGE_ODDS_DIFFERENCE", "ACCURACY_DIFFERENCE","Z_TEST_DIFFERENCE","ABROCA"]
            elif taskType == "REGRESSION":
                        methodList = ["DISPARATE IMPACT QUANTILE", "STATISTICAL PARITY QUANTILE", "NO DISPARATE IMPACT LEVEL",
                                    "AVERAGE SCORE DIFFERENCE", "ZSCORE DIFFERENCE", "MAX STATISTICAL PARITY", "STATISTICAL PARITY AUC"]
            elif taskType == "CLUSTERING":
                        methodList = ["CLUSTER BALANCE", "MINIMUM CLUSTER RATIO", "CLUSTER DISTRIBUTION KL", "CLUSTER DISTRIBUTION TOTAL VARIATION"]
            
            for method in methodList:
                List_metric_score = holisticaiMetrics[taskType][method](group_unprivileged, group_privileged,predicted_y, actual_y)
                if (method in list(ref_vals[taskType].keys())):
                    if List_metric_score["value"] != ref_vals[taskType][method]:
                        biased = True
                    else:
                        biased = False    
                List_metric_score["value"] = str(List_metric_score["value"])
                biased_list.append(biased)
                list_metric_results.append(List_metric_score)  
            # for i in range(len(holisticaiMetrics[taskType][methods])):
            #     List_metric_score = holisticaiMetrics[taskType][methods][i](group_unprivileged, group_privileged,
            #                                                                 predicted_y, actual_y)
            #     if (methods in list(ref_vals[taskType].keys())):
            #         if List_metric_score["value"] != ref_vals[taskType][methods]:
            #             biased = True
            #         else:
            #             biased = False
            #     elif methods == "Z_TEST_DIFFERENCE" or methods == "Z_TEST_RATIO":
            #         methods = "2SD Rule"
            #         if List_metric_score["value"] != ref_vals[taskType][methods]:
            #             biased = True
            #         else:
            #             biased = False
            #     elif methods == "NO DISPARATE IMPACT LEVEL":
            #         biased = False
            #     elif methods == "ALL":
            #         b_list = []
            #         if taskType == "BINARY CLASSIFICATION":
            #             methodList = ["STATISTICAL_PARITY", "DISPARATE_IMPACT", "FOUR_FIFTHS_RULE", "COHEN_D", "2SD Rule", "EQUALITY_OF_OPPORTUNITY_DIFFERENCE",
            #                         "FALSE_POSITIVE_RATE_DIFFERENCE", "AVERAGE_ODDS_DIFFERENCE", "ACCURACY_DIFFERENCE"]
            #         elif taskType == "REGRESSION":
            #             methodList = ["DISPARATE IMPACT QUANTILE", "STATISTICAL PARITY QUANTILE", "NO DISPARATE IMPACT LEVEL",
            #                         "AVERAGE SCORE DIFFERENCE", "ZSCORE DIFFERENCE", "MAX STATISTICAL PARITY", "STATISTICAL PARITY AUC"]
            #         elif taskType == "CLUSTERING":
            #             methodList = ["CLUSTER BALANCE", "MINIMUM CLUSTER RATIO", "CLUSTER DISTRIBUTION KL", "CLUSTER DISTRIBUTION TOTAL VARIATION"]
            #         for each in methodList:
            #             if each == "NO DISPARATE IMPACT LEVEL":
            #                 biased = False
            #             elif List_metric_score["value"] != ref_vals[taskType][each]:
            #                 biased = True
            #             else:
            #                 biased = False
            #             b_list.append(biased)
            #         if b_list.__contains__(True):
            #             biased = True

            #     List_metric_score["value"] = str(List_metric_score["value"])
            #     biased_list.append(biased)
            #     list_metric_results.append(List_metric_score)

        log.info("Biased List: ")
        log.info(biased_list)
        if True in biased_list:
            biased = True
        else:
            biased = False

        bias_list = []
        obj_biasresults = BiasResults(Biased=biased,
                                      protectedcAttrib=protected_list,
                                      metrics=list_metric_results)
        bias_list.append(obj_biasresults.biasResults)

        return (bias_list)


class MitigationResult:
    def mitigationResult(self, train_data, test_data, mitigationType, mitigationTechnique,original_data,column_names):
        group_unprivileged, group_privileged, predicted_y, actual_y,mitigated_df = mitigationTechniqueDict[mitigationType](
            train_data,
            test_data,
            mitigationTechnique,original_data,column_names)
        return group_unprivileged, group_privileged, predicted_y, actual_y,mitigated_df

    def mitigationResultList(self, bias_before_mitigation, bias_after_mitigation, original_metrics,
                             metric_post_mitigation,
                             biasType, mitigationType, mitigationTechnique,fileName):
        mitigation_results_list = []
        obj_mitigation_results = MitigationResults(biasType=biasType,
                                                   mitigation_type=mitigationType,
                                                   mitigation_technique=mitigationTechnique,
                                                   original_score_value_list=original_metrics,
                                                   original_bias_detected=bias_before_mitigation,
                                                   score_value_list=metric_post_mitigation,
                                                   bias_detected=bias_after_mitigation,
                                                   fileName=fileName
                                                   )
        mitigation_results_list.append(obj_mitigation_results.mitigationResults)

        return mitigation_results_list
    
    
    def preTrainmitigationResultList(self, bias_before_mitigation, bias_after_mitigation, original_metrics,
                             metric_post_mitigation,
                             biasType, mitigationType, mitigationTechnique,fileName):
        mitigation_results_list = []
        obj_mitigation_results = MitigationResults(biasType=biasType,
                                                   mitigation_type=mitigationType,
                                                   mitigation_technique=mitigationTechnique,
                                                   original_score_value_list=original_metrics,
                                                   original_bias_detected=bias_before_mitigation,
                                                   fileName=fileName
                                                   )
        mitigation_results_list.append(obj_mitigation_results.mitigationResults)

        return mitigation_results_list

class StandardDatasetDup(BinaryLabelDataset):
    def __init__(self, df, label_name, favorable_classes,
                 protected_attribute_names, privileged_classes,
                 instance_weights_name='', scores_name='',
                 categorical_features=[], features_to_keep=[],
                 features_to_drop=[], na_values=[], custom_preprocessing=None,
                 metadata=None):
        # 2. Perform dataset-specific preprocessing
        if custom_preprocessing:
            df = custom_preprocessing(df)

        # 3. Drop unrequested columns
        features_to_keep = features_to_keep or df.columns.tolist()
        keep = (set(features_to_keep) | set(protected_attribute_names)
              | set(categorical_features) | set([label_name]))
        keep=[col for col in keep if col!='']
        categorical_features=[col for col in categorical_features if col!='']
        if instance_weights_name!='':
            keep.append(instance_weights_name)
        df = df[sorted(set(keep) - set(features_to_drop), key=df.columns.get_loc)]
        categorical_features = sorted(set(categorical_features) - set(features_to_drop), key=df.columns.get_loc)

        # 4. Remove any rows that have missing data.
        dropped = df.dropna()
        count = df.shape[0] - dropped.shape[0]
        if count > 0:
            warning("Missing Data: {} rows removed from {}.".format(count,
                    type(self).__name__))
        df = dropped

        # 5. Create a one-hot encoding of the categorical variables.
        df = pd.get_dummies(df, columns=categorical_features, prefix_sep='=')

        # 6. Map protected attributes to privileged/unprivileged
        privileged_protected_attributes = []
        unprivileged_protected_attributes = []
        for attr, vals in zip(protected_attribute_names, privileged_classes):
            privileged_values = [1.]
            unprivileged_values = [0.]
            if callable(vals):
                df[attr] = df[attr].apply(vals)
            elif np.issubdtype(df[attr].dtype, np.number):
                # this attribute is numeric; no remapping needed
                privileged_values = vals
                unprivileged_values = list(set(df[attr]).difference(vals))
            else:
                # find all instances which match any of the attribute values
                priv = np.logical_or.reduce(np.equal.outer(vals, df[attr].to_numpy()))
                df.loc[priv, attr] = privileged_values[0]
                df.loc[~priv, attr] = unprivileged_values[0]

            privileged_protected_attributes.append(
                np.array(privileged_values, dtype=np.float64))
            unprivileged_protected_attributes.append(
                np.array(unprivileged_values, dtype=np.float64))

        # 7. Make labels binary
        favorable_label = 1.
        unfavorable_label = 0.
        if callable(favorable_classes):
            df[label_name] = df[label_name].apply(favorable_classes)
        elif np.issubdtype(df[label_name], np.number) and len(set(df[label_name])) == 2:
            # labels are already binary; don't change them
            favorable_label = favorable_classes[0]
            unfavorable_label = set(df[label_name]).difference(favorable_classes).pop()
        else:
            # find all instances which match any of the favorable classes
            pos = np.logical_or.reduce(np.equal.outer(favorable_classes, 
                                                      df[label_name].to_numpy()))
            df.loc[pos, label_name] = favorable_label
            df.loc[~pos, label_name] = unfavorable_label

        super(StandardDatasetDup, self).__init__(df=df, label_names=[label_name],
            protected_attribute_names=protected_attribute_names,
            privileged_protected_attributes=privileged_protected_attributes,
            unprivileged_protected_attributes=unprivileged_protected_attributes,
            instance_weights_name=instance_weights_name,
            scores_names=[scores_name] if scores_name else [],
            favorable_label=favorable_label,
            unfavorable_label=unfavorable_label, metadata=metadata)


class PRETRAIN:
    class Metrics_measuring_bias:
        def STATISTICAL_PARITY_DIFFERENCE(datalist):
            metric_scaled = BinaryLabelDatasetMetric(datalist['dataset_original'],
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)
            score = round(metric_scaled.statistical_parity_difference(), 2)
            obj_metric_sp = metricsEntity(name='STATISTICAL PARITY-DIFFERENCE',
                                          description='The difference in the rate of favorable outcomes received by unprivileged group to the privileged group. Ideal value for this is 0, which means there is no biasness present. Negative value for this means that the data is biased towards the privileged group and positive values means, it is biased towards the unprivileged group.',
                                          value=score)

            return obj_metric_sp.metricsEntity

        def DISPARATE_IMPACT(datalist):
            metric_scaled = BinaryLabelDatasetMetric(datalist['dataset_original'],
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)
            score = round(metric_scaled.disparate_impact(), 2)
            obj_metric_di = metricsEntity(name='DISPARATE-IMPACT',
                                          description='Ratio of the rate of favorable outcome for the unprivileged group to the privileged group. Ideal value is 1.',
                                          value=score)
            return obj_metric_di.metricsEntity
        
        def SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS(datalist):
            metric_scaled = BinaryLabelDatasetMetric(datalist['dataset_original'],
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)
            score = round(metric_scaled.smoothed_empirical_differential_fairness(), 2)
            obj_metric_sedf = metricsEntity(name='SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS',
                                          description='SED calculates the differential in the probability of favorable and unfavorable outcomes between intersecting groups divided by features. All intersecting groups are equal, so there are no unprivileged or privileged groups. The calculation produces a value between 0 and 1 that is the minimum ratio of Dirichlet smoothed probability for favorable and unfavorable outcomes between intersecting groups in the dataset.',
                                          value=score)

            return obj_metric_sedf.metricsEntity

        def CONSISTENCY(datalist):
            metric_scaled = BinaryLabelDatasetMetric(datalist['dataset_original'],
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)
            score = np.round(metric_scaled.consistency(), 2)
            obj_metric_cs = metricsEntity(name='CONSISTENCY',
                                          description='Individual fairness metric from [1]_ that measures how similar the labels are for similar instances.',
                                          value=score)

            return obj_metric_cs.metricsEntity
        
        def BASE_RATE(datalist):
            metric_scaled = BinaryLabelDatasetMetric(datalist['dataset_original'],
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)
            score = round(metric_scaled.base_rate(privileged=True), 2)
            obj_metric_di = metricsEntity(name='BASE_RATE',
                                          description='Compute the base rate, Pr(Y=1)=P/(P+N), optionally conditioned on protected attributes.',
                                          value=score)
            return obj_metric_di.metricsEntity

          


    class PREPROCESSING_MITIGATION:
        def preprocessing_mitigation(train_data, test_data, mitigationTechnique,original_data,column_names):
            if mitigationTechnique == "REWEIGHING":
                preprocessing_mitigator = Reweighing()
            elif mitigationTechnique == "DISPARATE IMPACT REMOVER":
                preprocessing_mitigator = preprocessing.DisparateImpactRemover(repair_level=1.0)
            elif mitigationTechnique == "CORRELATION REMOVER":
                preprocessing_mitigator = CorrelationRemover()
            elif mitigationTechnique == "LEARNING FAIR REPRESENTATION":
                preprocessing_mitigator = LearningFairRepresentation(k=4, Ax=0.2, Ay=2.0, Az=4.0, verbose=1)
            log.info("Preprocessing Mitigator: ", preprocessing_mitigator)
            X, y, group_a, group_b = train_data
            X_train=pd.DataFrame(X,columns=column_names)
            model = LogisticRegression(class_weight='balanced', solver='liblinear', random_state=42)
            pipeline = Pipeline(
                steps=[
                    ('scalar', StandardScaler()),
                    ("bm_preprocessing", preprocessing_mitigator),
                    ("model", model),
                ]
            )
            fit_params = {
                "bm__group_a": group_a,
                "bm__group_b": group_b
            }
            fit_params_ = {"group_a": group_a, "group_b": group_b}
            pipeline.fit(X,y,**fit_params)
            #save the mitigated train data by transforming intermidiate step.
            X_train_new=pipeline.named_steps["scalar"].transform(X)
            X_train_new=pipeline.named_steps["bm_preprocessing"].transform(X_train_new,y,**fit_params_) 
            X, y, group_a, group_b = test_data
            predict_params = {
                "bm__group_a": group_a,
                "bm__group_b": group_b,
            }
            fit_params_ = {"group_a": group_a, "group_b": group_b}
            y_pred = pipeline.predict(X, **predict_params)
            df1=pd.DataFrame(X_train_new,columns=column_names)
            #get mitigated data back in original format
            util=utils()
            new_dataset=util.get_mitigated_data(df1,original_data,False)
            return group_a, group_b, y_pred, y,new_dataset


class POSTTRAIN:
    class POSTPROCESSING_MITIGATION:
        def postprocessing_mitigation(train_data, test_data, mitigationTechnique,original_data,column_names):
            if mitigationTechnique == "ML DEBIASER": #int
                postprocessing_model = MLDebiaser()
            elif mitigationTechnique == "REJECT OPTION CLASSIFICATION":   #bool
                postprocessing_model = RejectOptionClassification(metric_name="Statistical parity difference")
            elif mitigationTechnique == "LP DEBIASER":
                postprocessing_model = LPDebiaserBinary()   #int
            elif mitigationTechnique == "EQUALIZED ODDS":
                postprocessing_model = EqualizedOdds(solver='highs', seed=42)  #int
            elif mitigationTechnique == "CALIBRATED EQUALIZED ODDS":
                postprocessing_model = CalibratedEqualizedOdds(cost_constraint="fnr")

            pipeline = Pipeline(
                steps=[
                    ('scalar', StandardScaler()),
                    ("estimator", LogisticRegression(random_state=42)),
                    ("bm_posprocessing", postprocessing_model),
                ]
            )

            X, y, group_a, group_b = train_data
            fit_params = {
                "bm__group_a": group_a,
                "bm__group_b": group_b
            }
           
            pipeline.fit(X, y, **fit_params)
           
            X, y, group_a, group_b = test_data
            predict_params = {
                "bm__group_a": group_a,
                "bm__group_b": group_b,
            }
            X_new=pipeline.named_steps["scalar"].transform(X)
            # scalar=StandardScaler()
            # X_new=scalar.transform(scalar)
            # X_new_df=pd.DataFrame()
            y_pred = pipeline.predict(X, **predict_params)
            log.info(y,)
            log.info("****************************************************y_pred")
            log.info(y_pred)
            log.info("------------------------------",np.array_equal(y_pred,y))
            X_new_df=pd.DataFrame(X_new,columns=column_names)
            X_new_df["labels_pred"]=y_pred
            util=utils()
            dataset=util.get_mitigated_data(X_new_df,original_data,True)
            return group_a, group_b, y_pred, y,dataset

    class Metrics_measuring_bias:
        class BINARY_CLASSIFICATION:
            def metrics_dict(self):
                binary_classification_metrics_dict = {
                    "Accuracy": metrics.accuracy_score,
                    "Balanced accuracy": metrics.balanced_accuracy_score,
                    "Precision": metrics.precision_score,
                    "Recall": metrics.recall_score,
                    "F1-Score": metrics.f1_score}
                return binary_classification_metrics_dict

            def ABROCA(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = abroca(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='ABROCA (area between roc curves).',
                                              description='This function computes the area between the roc curve of group_unprivileged and the roc curve of group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def ACCURACY_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = accuracy_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Accuracy Difference',
                                              description='This function computes the difference in accuracy of predictions for group_unprivileged and group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def AVERAGE_ODDS_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = average_odds_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Average Odds Difference',
                                              description='A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged. The range (-0.1,0.1) is considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def COHEN_D(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = cohen_d(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Cohen D',
                                              description='This function computes the Cohen D statistic (normalised statistical parity) between group_unprivileged and group_privileged.A value of 0 is desired. Negative values are unfair towards group_unprivileged. Positive values are unfair towards group_privileged. Reference values: 0.2 is considered a small effect size, 0.5 is considered medium, 0.8 is considered large.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def DISPARATE_IMPACT(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = disparate_impact(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Disparate Impact',
                                              description='This function computes the disparate impact (ratio of success rates) between privileeged and unprivileged.  value of 1 is desired. Values below 1 are unfair towards group_unprivileged. Values above 1 are unfair towards group_privileged. The range (0.8,1.2) is considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def EQUAL_OPPORTUNITY_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = equal_opportunity_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Equality of opportunity difference',
                                              description='This function computes the difference in true positive rates for group_unprivileged and group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def FALSE_NEGATIVE_RATE_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = false_negative_rate_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='False negative Rate difference',
                                              description='This function computes the difference in false negative rates for group_unprivileged and group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_privileged, and positive values indicating bias against group_unprivileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def FALSE_POSITIVE_RATE_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = false_positive_rate_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='False positive rate difference',
                                              description='This function computes the difference in false positive rates between group_unprivileged and group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def FOUR_FIFTHS(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = four_fifths(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Four Fifths',
                                              description='This function computes the four fifths rule (ratio of success rates) between group_unprivileged and group_privileged. The minimum of the ratio taken both ways is returned. A value of 1 is desired. Values below 1 are unfair. The range (0.8,1) is considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def STATISTICAL_PARITY(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = statistical_parity(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Statistical parity',
                                              description='This function computes the statistical parity (difference of success rates) between group_unprivileged and group_privileged. A value of 0 is desired. Negative values are unfair towards group_unprivileged. Positive values are unfair towards group_privileged. The range (-0.1,0.1) is considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def TRUE_NEGATIVE_RATE_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = true_negative_rate_diff(group_unprivileged, group_privileged, y_score, y_true)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='True negative Rate difference',
                                              description='This function computes the difference in true negative rates for group_unprivileged and group_privileged. A value of 0 is desired. This metric ranges between -1 and 1, with negative values indicating bias against group_unprivileged, and positive values indicating bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def Z_TEST_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = z_test_diff(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Z Test (Difference)',
                                              description='This function computes the Z-test statistic for the difference in success rates. Also known as 2-SD Statistic.A value of 0 is desired. This test considers the data unfair if the computed value is greater than 2 or smaller than -2, indicating a statistically significant difference in success rates.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def Z_TEST_RATIO(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = z_test_ratio(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Z Test (Ratio)',
                                              description='This function computes the Z-test statistic for the ratio in success rates. Also known as 2-SD Statistic. A value of 0 is desired. This test considers the data unfair if the computed value is greater than 2 or smaller than -2, indicating a statistically significant ratio in success rates.',
                                              value=score)

                return obj_metric_sp.metricsEntity

        class REGRESSION:
            def AVERAGE_SCORE_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = avg_score_diff(group_unprivileged, group_privileged, y_score, q=0)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Average Score Difference',
                                              description='This function computes the difference in average scores between '
                                                          'group_unprivileged and group_privileged.A value of 0 is desired. '
                                                          'Negative values indicate the group_unprivileged has lower average '
                                                          'score, so bias against group_unprivileged. Positive values '
                                                          'indicate group_privileged has lower average score, so bias against '
                                                          'group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def CORRELATION_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = correlation_diff(group_unprivileged, group_privileged, y_score, y_true, q=0)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Correlation difference',
                                              description='This function computes the difference in correlation between '
                                                          'predictions and targets for group_unprivileged and group_privileged.'
                                                          'A value of 0 is desired. This metric ranges between -2 and 2, '
                                                          'with -1 indicating strong bias against group_unprivileged, and +1 '
                                                          'indicating strong bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def DISPARATE_IMPACT_REGRESSION(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = disparate_impact_regression(group_unprivileged, group_privileged, y_score, q=0.8)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Disparate Impact quantile (Regression version)',
                                              description='This function computes the ratio of success rates between '
                                                          'group_unprivileged and group_b, where success means predicted score '
                                                          'exceeds a given quantile (default = 0.8). A value of 1 is desired. '
                                                          'Values below 1 are unfair towards group_unprivileged. Values above 1 '
                                                          'are unfair towards group_privileged. The range (0.8,1.2) is '
                                                          'considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def MAE_RATIO(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = mae_ratio(group_unprivileged, group_privileged, y_score, y_true, q=0)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='MAE ratio',
                                              description='This function computes the ratio of the MAE for group_unprivileged '
                                                          'and group_privileged. A value of 1 is desired. Lower values show '
                                                          'bias against group_unprivileged. Higher values show bias against '
                                                          'group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def MAX_ABSOLUTE_STATISTICAL_PARITY(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = max_statistical_parity(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Max absolute statistical parity',
                                              description='This function computes the maximum over all thresholds of the '
                                                          'absolute statistical parity between group_unprivileged and '
                                                          'group_privileged. A value of 0 is desired. Values below 0.1 in '
                                                          'absolute value are considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def NO_DISPARATE_IMPACT_LEVEL(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = no_disparate_impact_level(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='No disparate impact level',
                                              description='This function computes the maximum score such that thresholding at '
                                                          'that score does not allow adverse impact.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def RMSE_RATIO(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = rmse_ratio(group_unprivileged, group_privileged, y_score, y_true, q=0)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='RMSE ratio',
                                              description='This function computes the ratio of the RMSE for '
                                                          'group_unprivileged and group_privileged. A value of 1 is desired. '
                                                          'Lower values show bias against group_unprivileged. Higher values '
                                                          'show bias against group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def STATISTICAL_PARITY_AUC(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = statistical_parity_auc(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Statistical parity (Area Under Curve)',
                                              description='This function computes the area under the statistical parity '
                                                          'versus threshold curve. A value of 0 is desired. Values below '
                                                          '0.075 are considered acceptable.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def STATISTICAL_PARITY_QUANTILE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = statistical_parity_regression(group_unprivileged, group_privileged, y_score, q=0.5)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Statistical Parity quantile (Regression version)',
                                              description='This function computes the difference of success rates between '
                                                          'group_unprivileged and group_privileged, where success means that '
                                                          'the predicted score exceeds a given quantile. A value of 0 is '
                                                          'desired. Values below 0 are unfair towards group_unprivileged. '
                                                          'Values above 0 are unfair towards group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def ZSCORE_DIFFERENCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = zscore_diff(group_unprivileged, group_privileged, y_score, q=0)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='ZScore Difference',
                                              description='This function computes the spread in Zscores between '
                                                          'group_unprivileged and group_privileged. The Zscore is a '
                                                          'normalised version of Disparate Impact. A value of 0 is desired. '
                                                          'The Zscore will approximate the number of standard deviations away '
                                                          'from the mean. In particular values that exceed 2 are '
                                                          'statistically significant with 95% probability.',
                                              value=score)

                return obj_metric_sp.metricsEntity

        class CLUSTERING:
            def CLUSTER_BALANCE(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = cluster_balance(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Cluster Balance',
                                              description='Given a clustering and protected attribute. The cluster balance is '
                                                          'the minimum over all groups and clusters of the ratio of the '
                                                          'representation of members of that group in that cluster to the '
                                                          'representation overall. A value of 1 is desired. That is when all '
                                                          'clusters have the exact same representation as the data. Lower '
                                                          'values imply the existence of clusters where either '
                                                          'group_unprivileged or group_privileged is underrepresented.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def CLUSTER_DIST_KL(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = cluster_dist_kl(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Cluster Distribution KL',
                                              description='This function computes the distribution of group_unprivileged and '
                                                          'group_privileged membership across the clusters. It then returns '
                                                          'the KL distance from the distribution of group_unprivileged to the '
                                                          'distribution of group_privileged. A value of 0 is desired. That '
                                                          'indicates that both groups are distributed similarly amongst the '
                                                          'clusters. Higher values indicate the distributions of both groups '
                                                          'amongst the clusters differ more.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def CLUSTER_DIST_L1(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = cluster_dist_l1(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Cluster Distribution Total Variation',
                                              description='This function computes the distribution of group_unprivileged and '
                                                          'group_privileged across clusters. It then outputs the total '
                                                          'variation distance between these distributions.A value of 0 is '
                                                          'desired. That indicates that both groups are distributed similarly '
                                                          'amongst the clusters. The metric ranges between 0 and 1, '
                                                          'with higher values indicating the groups are distributed in very '
                                                          'different ways.',
                                              value=score)

                return obj_metric_sp.metricsEntity

            def MIN_CLUSTER_RATIO(group_unprivileged, group_privileged, y_score, y_true):
                metric_scaled = min_cluster_ratio(group_unprivileged, group_privileged, y_score)
                score = round(metric_scaled, 3)
                obj_metric_sp = metricsEntity(name='Minimum Cluster Ratio',
                                              description='Given a clustering and protected attributes. The min cluster ratio '
                                                          'is the minimum over all clusters of the ratio of number of '
                                                          'group_unprivileged members to the number of group_privileged '
                                                          'members. A value of 1 is desired. That is when all clusters are '
                                                          'perfectly balanced. Low values imply the existence of clusters '
                                                          'where group_unprivileged has fewer members than group_privileged.',
                                              value=score)

                return obj_metric_sp.metricsEntity


prelist = [PRETRAIN.Metrics_measuring_bias.STATISTICAL_PARITY_DIFFERENCE,
           PRETRAIN.Metrics_measuring_bias.DISPARATE_IMPACT,
           PRETRAIN.Metrics_measuring_bias.SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS,
           PRETRAIN.Metrics_measuring_bias.BASE_RATE]
           

methoddict = {
    "PRETRAIN": {"STATISTICAL-PARITY-DIFFERENCE": [PRETRAIN.Metrics_measuring_bias.STATISTICAL_PARITY_DIFFERENCE],
                 "DISPARATE-IMPACT": [PRETRAIN.Metrics_measuring_bias.DISPARATE_IMPACT],
                 "SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS": [PRETRAIN.Metrics_measuring_bias.SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS],
                 "BASE_RATE":[PRETRAIN.Metrics_measuring_bias.BASE_RATE],
                 "ALL": prelist}}

post_metric_dict = {
    "BINARY CLASSIFICATION": [POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.STATISTICAL_PARITY,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.DISPARATE_IMPACT,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FOUR_FIFTHS,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.COHEN_D,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.Z_TEST_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.AVERAGE_ODDS_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.EQUAL_OPPORTUNITY_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FALSE_NEGATIVE_RATE_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FALSE_POSITIVE_RATE_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.TRUE_NEGATIVE_RATE_DIFFERENCE,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.ABROCA,
                              POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.ACCURACY_DIFFERENCE],
    "REGRESSION": [POSTTRAIN.Metrics_measuring_bias.REGRESSION.DISPARATE_IMPACT_REGRESSION,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.STATISTICAL_PARITY_QUANTILE,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.NO_DISPARATE_IMPACT_LEVEL,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.AVERAGE_SCORE_DIFFERENCE,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.ZSCORE_DIFFERENCE,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.MAX_ABSOLUTE_STATISTICAL_PARITY,
                   POSTTRAIN.Metrics_measuring_bias.REGRESSION.STATISTICAL_PARITY_AUC],
    "CLUSTERING": [POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_BALANCE,
                   POSTTRAIN.Metrics_measuring_bias.CLUSTERING.MIN_CLUSTER_RATIO,
                   POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_DIST_KL,
                   POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_DIST_L1]
}
holisticaiMetrics = {"BINARY CLASSIFICATION": {
                                              "ALL": post_metric_dict["BINARY CLASSIFICATION"],
                                               "COHEN_D": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.COHEN_D,
                                               "DISPARATE_IMPACT": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.DISPARATE_IMPACT,
                                               "FOUR_FIFTHS_RULE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FOUR_FIFTHS,
                                               "STATISTICAL_PARITY": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.STATISTICAL_PARITY,
                                               "Z_TEST_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.Z_TEST_DIFFERENCE,
                                               "Z_TEST_RATIO": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.Z_TEST_RATIO,
                                               "AVERAGE_ODDS_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.AVERAGE_ODDS_DIFFERENCE,
                                               "EQUAL_OPPORTUNITY_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.EQUAL_OPPORTUNITY_DIFFERENCE,
                                               "FALSE_NEGATIVE_RATE_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FALSE_NEGATIVE_RATE_DIFFERENCE, 
                                               "FALSE_POSITIVE_RATE_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.FALSE_POSITIVE_RATE_DIFFERENCE,
                                               "TRUE_NEGATIVE_RATE_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.TRUE_NEGATIVE_RATE_DIFFERENCE,
                                               "ABROCA": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.ABROCA,
                                               "ACCURACY_DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.BINARY_CLASSIFICATION.ACCURACY_DIFFERENCE},
                     "REGRESSION": {
                         "AVERAGE SCORE DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.AVERAGE_SCORE_DIFFERENCE,
                         "CORRELATION DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.CORRELATION_DIFFERENCE,
                         "DISPARATE IMPACT QUANTILE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.DISPARATE_IMPACT_REGRESSION,
                         "MAE RATIO": POSTTRAIN.Metrics_measuring_bias.REGRESSION.MAE_RATIO,
                         "MAX STATISTICAL PARITY": POSTTRAIN.Metrics_measuring_bias.REGRESSION.MAX_ABSOLUTE_STATISTICAL_PARITY,
                         "NO DISPARATE IMPACT LEVEL": POSTTRAIN.Metrics_measuring_bias.REGRESSION.NO_DISPARATE_IMPACT_LEVEL,
                         "ALL": post_metric_dict["REGRESSION"],
                         "RMSE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.RMSE_RATIO,
                         "STATISTICAL PARITY AUC": POSTTRAIN.Metrics_measuring_bias.REGRESSION.STATISTICAL_PARITY_AUC,
                         "STATISTICAL PARITY QUANTILE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.STATISTICAL_PARITY_QUANTILE,
                         "ZSCORE DIFFERENCE": POSTTRAIN.Metrics_measuring_bias.REGRESSION.ZSCORE_DIFFERENCE},
                     "CLUSTERING": {"CLUSTER BALANCE": POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_BALANCE,
                                    "CLUSTER DISTRIBUTION KL": POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_DIST_KL,
                                    "CLUSTER DISTRIBUTION TOTAL VARIATION": POSTTRAIN.Metrics_measuring_bias.CLUSTERING.CLUSTER_DIST_L1,
                                    "ALL": post_metric_dict["CLUSTERING"],
                                    "MINIMUM CLUSTER RATIO": POSTTRAIN.Metrics_measuring_bias.CLUSTERING.MIN_CLUSTER_RATIO}
                     }

mitigationTechniqueDict = {
    "PREPROCESSING": PRETRAIN.PREPROCESSING_MITIGATION.preprocessing_mitigation,
    "POSTPROCESSING": POSTTRAIN.POSTPROCESSING_MITIGATION.postprocessing_mitigation
}
class EstimatorsList:
    estimators={
        "randomforestclassifier": RandomForestClassifier(random_state=42),
        "logisticregression": LogisticRegression(random_state=42),
        "adaBoostclassifier": AdaBoostClassifier(random_state=42),
        "gradientboostingclassifier": GradientBoostingClassifier(random_state=42),
        "decisiontreeclassifier": DecisionTreeClassifier(random_state=42),
        "kneighborsclassifier": KNeighborsClassifier(),
    }
# Statistical Parity Difference: The difference in the rate of favorable outcomes received by unprivileged group to the privileged group. Ideal value for this is 0, which means there is no biasness present. Negative value for this means that the data is biased towards the privileged group and positive values means, it is biased towards the unprivileged group.
# Disparate Impact: Ratio of the rate of favorable outcome for the unprivileged group to the privileged group. Ideal value is 1.
# Equal opportunity difference: Difference of the True Positive Rate of unprivileged group to the privileged group. Ideal value for no bias present is 0.
# Average odds difference: The average difference of false positive rate and true positive rate between unprivileged group to the privileged group. Ideal value is 0.
