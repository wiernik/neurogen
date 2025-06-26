import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# load original dataset
df = pd.read_csv(r'c:\Users\lydia\L3_HIPAA_LENA\metadata\children.csv')

# remove groups we're not looking at
for_removal = ['environmental_risk', 'autism_spectrum_disorder']
df_cleaned = df[~df['group_id'].isin(for_removal)]

# overall gender distribution
overall = df_cleaned['child_sex'].value_counts()
print(overall)

# gender distribution by group_id
by_group = df_cleaned.groupby('group_id')['child_sex'].value_counts().unstack(fill_value=0)
by_group['Total'] = by_group.sum(axis=1)
print("\nGender distribution by group_id with totals:")
print(by_group)

#calculate age ranges per group

#first convert child_dob to datetime
def calculate_age_in_months(dob_str):
    dob = pd.to_datetime(dob_str, format='%Y-%m-%d', errors='coerce')
    today = pd.to_datetime(date.today())
    if pd.isnull(dob):
        return None
    rd = relativedelta(today, dob)
    return rd.years * 12 + rd.months

df_cleaned['age_months'] = df_cleaned['child_dob'].apply(calculate_age_in_months)

age_ranges_by_group = df_cleaned.groupby('group_id')['age_months'].agg(['min', 'max', 'mean', 'median', 'std']).round(1)
print("\nAge (in months) ranges by group_id:")
print(age_ranges_by_group)

#save output
overall.to_csv('overall_gender_distribution.csv', header=True)
by_group.to_csv('gender_distribution_by_group.csv')
age_ranges_by_group.to_csv('age_ranges_by_group.csv')



