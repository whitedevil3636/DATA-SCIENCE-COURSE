import pandas as pd
import streamlit as st
from sklearn.impute import SimpleImputer
from fancyimpute import IterativeImputer

from sklearn.preprocessing import LabelEncoder

from io import StringIO

from sklearn.feature_selection import SelectKBest, chi2 , f_classif , mutual_info_classif
from sklearn.feature_selection import VarianceThreshold


def analyze_csv_file(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = st.session_state.get('df', df)

        if 'columns_removed' not in st.session_state:
            st.write(f"**Columns:** {list(df.columns)}")

            selected_columns = st.multiselect("Select columns to remove", options=df.columns)

            if st.button("Remove Selected Columns"):
                if selected_columns:
                    df = df.drop(columns=selected_columns)

                    st.session_state['df'] = df

                    st.session_state['columns_removed'] = True

                    st.success(f"Columns removed: {', '.join(selected_columns)}")

                    st.write("### DataFrame After Removing Selected Columns")
                    st.write(df)
            

        missing_values = df.isnull().sum()
        has_missing_values = missing_values.sum() > 0

        duplicate_count = df.duplicated().sum()
        has_duplicates = duplicate_count > 0

        if has_missing_values or has_duplicates:
            st.warning("There are missing/duplicated values with the uploaded CSV file")

            if has_missing_values:
                st.write("### Missing Values")
                st.write(missing_values[missing_values > 0])
                
                # Options for handling missing values
                for column in missing_values[missing_values > 0].index:
                    st.write(f"#### Column: {column}")
                    
                    # Option to remove missing values
                    if st.button(f"Remove rows with missing values in '{column}'"):

                        df = df.dropna(subset=[column])
                        st.session_state['df'] = df
                        st.success(f"Rows with missing values in '{column}' removed successfully.")
                        
                    # Fill with mean
                    if st.button(f"Fill missing values in '{column}' with mean"):

                        imputer = SimpleImputer(strategy='mean')
                        df[column] = imputer.fit_transform(df[[column]])

                        st.session_state['df'] = df
                        st.success(f"Missing values in '{column}' filled with mean.")

                    # Fill with median
                    if st.button(f"Fill missing values in '{column}' with median"):
                        imputer = SimpleImputer(strategy='median')
                        df[column] = imputer.fit_transform(df[[column]])
                        st.session_state['df'] = df
                        st.success(f"Missing values in '{column}' filled with median.")
                        
                    # Fill with mode
                    if st.button(f"Fill missing values in '{column}' with mode"):

                        mode_value = df[column].mode()[0]
                        df[column].fillna(mode_value, inplace=True)

                        st.session_state['df'] = df
                        st.success(f"Missing values in '{column}' filled with mode.")
                        
                    # Fill with custom value
                    custom_value = st.text_input(f"Custom value to fill missing values in '{column}'")
                    if st.button(f"Fill missing values in '{column}' with custom value"):
                        if custom_value:
                            df[column].fillna(custom_value, inplace=True)
                            st.session_state['df'] = df
                            st.success(f"Missing values in '{column}' filled with custom value.")
                        else:
                            st.warning("Please provide a custom value.")
                        
                    # Iterative Imputation (MICE)
                    if st.button(f"Apply Iterative Imputation for '{column}'"):
                        imputer = IterativeImputer()
                        df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
                        st.session_state['df'] = df_imputed
                        st.success(f"Iterative Imputation applied successfully.")

            if has_duplicates:
                st.write("### Duplicate Values")
                st.write(f"**Number of duplicate rows:** {duplicate_count}")
                
                if st.button("Remove Duplicate Rows"):
                    df = df.drop_duplicates()
                    st.session_state['df'] = df
                    st.success("Duplicate rows removed successfully.")

                    duplicate_count = df.duplicated().sum()
                    st.write(duplicate_count)

        show_details = st.checkbox("Show Details")

        if show_details:
            st.write("### Basic Information")
            st.write(f"**Number of columns:** {df.shape[1]}")
            st.write(f"**Column names:** {list(df.columns)}")

            st.write("### Column Data Types")
            st.write(df.dtypes)

            st.write("### Missing Values")
            st.write(missing_values[missing_values > 0])

            st.write("### Duplicate Values")
            st.write(f"**Number of duplicate rows:** {duplicate_count}")


def transform_object_columns(df):
    label_encoders = {}

    for column in df.select_dtypes(include=['object']).columns:  #Gender,Embarked

        le = LabelEncoder()
        df[column] = le.fit_transform(df[column].astype(str))

        label_encoders[column] = le

    return df, label_encoders
            

def select_target_column(df):
    if df is not None:
        target_column = st.selectbox("Select Target Column", [""] + list(df.columns), index=0)
        if target_column != "":

            X = df.drop(columns=[target_column])
            Y = df[target_column]

            st.session_state['X'] = X
            st.session_state['Y'] = Y

            st.success(f"Target column '{target_column}' selected successfully.")
            st.write("### Input Features (X)")
            st.write(X)
            st.write("### Target Feature (Y)")
            st.write(Y)

def feature_selection_options():
    feature_selection_method = st.selectbox(
        "Select Feature Selection Method",
        ["None", "Correlation Coefficient", "Chi-Square Test", "ANOVA", "Mutual Information", "Variance Threshold"],
        index=0
    )

    st.session_state['feature_selection_method'] = feature_selection_method

    if feature_selection_method != "None":
        st.success(f"'{feature_selection_method}' selected for feature selection.")
    else:
        st.info("No feature selection method selected.")

def correlation_coefficient_selection():
    if 'df' in st.session_state and 'Y' in st.session_state:
        df = st.session_state['df']
        Y = st.session_state['Y']
  
        threshold = st.slider("Select Correlation Coefficient Threshold", 0.0, 1.0, 0.5)
        
        if st.button("Apply Correlation Coefficient"):

            corr_matrix = df.corrwith(Y)
            
            selected_features = corr_matrix[abs(corr_matrix) >= threshold].index.tolist()
            
            selected_features = [feature for feature in selected_features if feature != Y.name]
            
            st.write(f"### Selected Features (Correlation Coefficient >= {threshold})")
            st.write(selected_features)
            
            if selected_features:
                st.session_state['selected_features'] = selected_features
                st.success("Features selected based on correlation coefficient.")
            else:
                st.warning("No features selected based on the given threshold.")

        save_selected_features()


def save_selected_features():
    if 'selected_features' in st.session_state and 'Y' in st.session_state:
        df = st.session_state['df']
        selected_features = st.session_state['selected_features']
        Y = st.session_state['Y']

        # Create a new DataFrame with selected features and target column
        new_df = pd.concat([df[selected_features], Y], axis=1)

        # Show the new DataFrame to the user
        st.write("### New DataFrame with Selected Features and Target Column")
        st.write(new_df)

        # Convert DataFrame to CSV format
        csv = new_df.to_csv(index=False)
        buffer = StringIO(csv)

        # Provide download option
        st.download_button(
            label="Download CSV",
            data=buffer.getvalue(),
            file_name='selected_features_and_target.csv',
            mime='text/csv'
        )


def chi_square_selection():
    if 'X' in st.session_state and 'Y' in st.session_state:
        X = st.session_state['X']
        Y = st.session_state['Y']
        
        # Slider for number of top features to select
        k = st.slider("Select the number of top features to keep", 1, X.shape[1], X.shape[1])

        # Apply SelectKBest with chi2
        selector = SelectKBest(score_func=chi2, k=k)
        X_new = selector.fit_transform(X, Y)

        # Get selected feature indices
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()

        # Display selected features
        st.write(f"### Selected Features : ")
        st.write(selected_features)

        # Update session state
        st.session_state['selected_features'] = selected_features

        st.success("Features selected based on Chi-Square test.")
        
        # Provide download option
        save_selected_features()

def anova_selection():
    if 'X' in st.session_state and 'Y' in st.session_state:
        X = st.session_state['X']
        Y = st.session_state['Y']
        
        # Slider for number of top features to select
        k = st.slider("Select the number of top features to keep", 1, X.shape[1], X.shape[1])

        # Apply SelectKBest with f_classif (ANOVA)
        selector = SelectKBest(score_func=f_classif, k=k)
        X_new = selector.fit_transform(X, Y)

        # Get selected feature indices
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()

        # Display selected features
        st.write(f"### Selected Features:")
        st.write(selected_features)

        # Update session state
        st.session_state['selected_features'] = selected_features
        st.success("Features selected based on ANOVA.")
        
        # Provide download option
        save_selected_features()

def mutual_information_selection():
    if 'X' in st.session_state and 'Y' in st.session_state:
        X = st.session_state['X']
        Y = st.session_state['Y']
        
        k = st.slider("Select the number of top features to keep", 1, X.shape[1], X.shape[1])
        selector = SelectKBest(score_func=mutual_info_classif, k=k)
        X_new = selector.fit_transform(X, Y)

        # Get selected feature indices
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()

        # Display selected features
        st.write(f"### Selected Features:")
        st.write(selected_features)

        # Update session state
        st.session_state['selected_features'] = selected_features
        st.success("Features selected based on Mutual Information.")
        
        # Provide download option
        save_selected_features()

def variance_threshold_selection():
    if 'X' in st.session_state:
        X = st.session_state['X']
        
        # Slider for setting the variance threshold
        threshold = st.slider("Select the variance threshold", 0.0, 1.0, 0.0)
        
        # Apply VarianceThreshold
        selector = VarianceThreshold(threshold=threshold)
        X_new = selector.fit_transform(X)

        # Get selected feature indices
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()

        # Display selected features
        st.write(f"### Selected Features:")
        st.write(selected_features)

        # Update session state
        st.session_state['selected_features'] = selected_features
        st.success("Features selected based on Variance Threshold.")
        
        # Provide download option
        save_selected_features()


                

