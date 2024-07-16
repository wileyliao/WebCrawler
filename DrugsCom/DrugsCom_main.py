from DrugCom_WebOperations import (
    initialize_driver,
    send_input, clear_input,
    wait_and_get_element, click_element,
    extract_info,
    dialogs_check,
    restart_driver
)
from DrugCom_df_processing import load_data, save_data, mark_skipped_drugs
import DrugCom_config

from selenium.webdriver.common.by import By
import pandas as pd
driver = initialize_driver()

def search_pairs(driver, drug_1, drug_2, skipped_drugs):
    try:
        input_box = wait_and_get_element(driver, By.ID, 'livesearch-interaction-basic', 20)
        print(f'keying {drug_1}.......')
        send_input(input_box, drug_1)
        error_drug = dialogs_check(driver, By.ID, 'ddc-modal', 'open', drug_1)
        if error_drug:
            skipped_drugs.add(error_drug)
            return error_drug
        input_box = wait_and_get_element(driver, By.ID, 'livesearch-interaction', 20)
        print(f'deleting input ......')
        clear_input(input_box)
        print(f'keying {drug_2}.......')
        send_input(input_box, drug_2)
        error_drug = dialogs_check(driver, By.ID, 'ddc-modal', 'open', drug_2)
        if error_drug:
            skipped_drugs.add(error_drug)
            return error_drug

    except Exception:
        raise

def main():
    global driver
    driver = initialize_driver()
    df = load_data(config.FILE_NAME)
    driver.get(config.URL)
    wait_and_get_element(driver, By.ID, 'livesearch-interaction-basic', 20)
    skipped_drugs = set()
    count = 0

    for index, row in df.iterrows():
        try:
            if pd.notna(row['interactions_DrugCom']):
                print(f'{index}: Skipped as interactions already have value')
                continue

            print(f'-----------round{count}----------')

            if count > 8:
                print('Restart.......')
                driver = restart_driver(driver, config.URL)
                count = 0

            drug_1 = row['drug_1']
            drug_2 = row['drug_2']

            if drug_1 in skipped_drugs or drug_2 in skipped_drugs:
                skipped_drug = drug_1 if drug_1 in skipped_drugs else drug_2
                mark_skipped_drugs(df, index, f'{skipped_drug} No results')
                print(f'{index}: Skipped {skipped_drug} as it was previously found to have no results')
                continue

            interaction_checker_link = wait_and_get_element(
                driver,
                By.XPATH,
                '//a[@href="/drug_interactions.html" and contains(text(), "Interaction Checker")]'
                , 10
            )

            click_element(driver, interaction_checker_link)
            error_drug = search_pairs(driver, drug_1, drug_2, skipped_drugs)

            if error_drug:
                mark_skipped_drugs(df, index, f'{error_drug} No results')
                print(f"{index}: Skipped {error_drug} as it is not found")
                continue

            count += 1

            print("Getting interactions")
            check_interactions_link = wait_and_get_element(driver, By.LINK_TEXT, 'Check Interactions', 5)
            click_element(driver, check_interactions_link)
            professional_link = wait_and_get_element(driver, By.LINK_TEXT, 'Professional', 5)
            click_element(driver, professional_link)
            interactions = extract_info(driver, By.CSS_SELECTOR, '.interactions-reference p', 20)

            print(interactions)
            df.at[index, 'interactions_DrugCom'] = interactions
            save_data(df, config.FILE_NAME)

        except Exception as e:
            print(f'Exception encountered in main loop: {e}')
            df.at[index, 'interactions_DrugCom'] = 'No results'
            save_data(df, config.FILE_NAME)
            driver = restart_driver(driver, config.URL)
            count = 0

if __name__ == "__main__":
    main()
    driver.quit()