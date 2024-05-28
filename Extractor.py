from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import itertools
from pprint import pprint
import threading
from webdriver_manager.chrome import ChromeDriverManager

def set_driver():
    # options = uc.ChromeOptions()
    # options.add_argument("--headless")  # Set to True for headless mode
    # options.add_argument("--disable-gpu")

    driver = uc.Chrome()
    # url = "https://life.gocompare.com/life/"
    # url = "https://www.zip-codes.com/m/state/fl.asp"
    # url ="https://www.zip-codes.com/m/state/pr.asp"
    # html = driver.page_source

    # driver.quit()
    # return html
    return driver


def actions(driver, zipcode, mode="physician"):
    if mode == "physician":
        url = "https://www.medicare.gov/care-compare/?providerType=Physician"
    elif mode == "hospitals":
        url = "https://www.medicare.gov/care-compare/?providerType=Hospital"
    driver.get(url)
    driver.set_window_size(928, 1032)
    driver.execute_script("window.scrollTo(0,0)")
    # driver.find_element(By.ID, "mat-input-2").click()
    driver.execute_script("window.scrollTo(0,386)")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="Street, ZIP code, city, or state"]'))).send_keys(zipcode)
    # driver.find_element(By.CSS_SELECTOR, ".highlight").click()
    select = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//mat-option/span/span/span"))
    )
    select.click()
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ProviderSearchSearchButton__submit-text_wrapper"))
    )
    search.click()
    # driver.execute_script("window.scrollTo(0,0)")
    # driver.execute_script("window.scrollTo(0,362)")
    # driver.execute_script("window.scrollTo(0,3992)")
    allclick = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, "All"))
    )
    allclick.click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.ProviderSearchResultCardContainer__details-link')
    links = []
    for div in div_elements:
        try:
            a_tag = div.find_element(By.CSS_SELECTOR, 'a')
            links.append(a_tag.get_attribute('href'))
        except:
            pass

    return links


def extract(driver, links, zipcode):
    names = []
    addresses_1 = []
    addresses_2 = []
    provider_numbers_1 = []
    provider_numbers_2 = []
    specialties = []
    consetions = []
    genders = []
    educations = []
    urls = []

    i = 1

    for url in links:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        print(f"{i}/{len(links)} | url => {url}")
        urls.append(url)

        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ProviderDetailsHeroContainer__title-name")))

        try:
            name = soup.find('h1', class_='ProviderDetailsHeroContainer__title-name').text.strip()
            names.append(name)
            print(f"Name => {name}")
        except:
            names.append("null")
        # try:
        #     group_link = soup.find('a', class_='ng-star-inserted').text.strip()
        #     group_links.append(group_link)
        #     print(f"Group Link => {group_link}")
        # except:
        #     group_links.append("null")

        # ADDRESSES!!!
        try:
            address_divs = soup.find_all('div', class_='ProviderDetailsLocations__address')
            if len(address_divs) == 2:
                print(f"Address_1 => {address_divs[0].get_text(strip=True)}")
                print(f"Address_2 => {address_divs[1].get_text(strip=True)}")
                addresses_1.append(address_divs[0].get_text(strip=True))
                addresses_2.append(address_divs[1].get_text(strip=True))
            else:
                print(f"Address_1 => {address_divs[0].get_text(strip=True)}")
                addresses_1.append(address_divs[0].get_text(strip=True))
                addresses_2.append("null")
        except:
            addresses_1.append("null")
            addresses_2.append("null")

        # PHONE NUMBERS!!!
        try:
            provider_number_div = soup.find_all('div', class_='ProviderDetailsLocations__phone')
            if len(provider_number_div) == 2:
                print(f"Provider Number_1 => {provider_number_div[0].get_text(strip=True)}")
                print(f"Provider Number_2 => {provider_number_div[1].get_text(strip=True)}")
                provider_numbers_1.append(provider_number_div[0].get_text(strip=True))
                provider_numbers_2.append(provider_number_div[1].get_text(strip=True))
            else:
                print(f"Provider Number_1 => {provider_number_div[0].get_text(strip=True)}")
                provider_numbers_1.append(provider_number_div[0].get_text(strip=True))
                provider_numbers_2.append("null")
        except:
            provider_numbers_1.append("null")
            provider_numbers_2.append("null")
        try:
            specialty = soup.find('div', class_='ProviderDetailsOverview__specialties').text.strip()
            result = specialty.replace("Specialties", "")

            specialties.append(result)
            print(f"Specialty => {result}")
        except:
            specialties.append("null")

        try:
            div_sex_list = soup.find_all('div', text='Sex')
            for div_sex in div_sex_list:
                sex_text = div_sex.find_next_sibling('p').text.strip()
                print(f"Sex => {sex_text}")
            genders.append(sex_text)

        except:
            genders.append("null")

        try:
            education = soup.find('div', text='Education & training').find_next_sibling('p').text.strip()
            educations.append(education)
            print(f"Education => {education}")
        except:
            educations.append("null")

        try:
            consetion = soup.find('div', class_='ProviderDetailsPhysicianHero__additional-info').text.strip()
            consetions.append(consetion)
            print(f"Consetion => {consetion}")
        except:
            consetions.append("null")

        print("----------------------------------------------------------")
        i += 1

    # Create a pandas DataFrame
    data = {
        'name': names,
        'address_1': addresses_1,
        'address_2': addresses_2,
        'provider number 1': provider_numbers_1,
        'provider number 2': provider_numbers_2,
        'specialties': specialties,
        'consetion': consetions,
        'educations': educations,
        'genders': genders,
        'zipcode': zipcode,
        'url': urls
    }

    return data


def extract_hospitals(links, zipcode):
    names = []
    addresses = []
    provider_numbers = []
    qualities = []
    hospital_types = []
    emergency_services = []
    urls = []
    patient_survey_ratings = []
    hospital_ratings = []

    i = 1

    for url in links:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        print(f"{i}/{len(links)} | url => {url}")
        urls.append(url)

        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ProviderDetailsHeroContainer__title-name")))

        try:
            name = soup.find('h1', class_='ProviderDetailsHeroContainer__title-name').text.strip()
            names.append(name)
            print(f"Name => {name}")
        except:
            names.append("null")

        try:
            qualities_parent = soup.find_all('div',
                                             class_='d-flex justify-content-between ProviderDetailsMeasuresMenuSection__indicator')
            qualities_texts = [h3.text.strip() for quality in qualities_parent for h3 in quality.find_all('h3')]
            qualities_text = ', '.join(qualities_texts)
            print(f"Qualities => {qualities_text}")
            qualities.append(qualities_text)
        except:
            qualities.append("null")

        try:
            hospital_type = soup.find('div', text='Hospital type').find_next_sibling('p').text.strip()
            print(f"Hospital Type: {hospital_type}")
            hospital_types.append(hospital_type)
        except:
            hospital_types.append("null")

        try:
            emergency_service = soup.find('div', text='Provides emergency services?').find_next_sibling(
                'ccxp-yes-no').find('div').find('span').text.strip()
            print(f"Emergency Services: {emergency_service}")
            emergency_services.append(emergency_service)
        except:
            emergency_services.append("null")

        try:
            address_divs = soup.find_all('div', class_='ProviderDetailsLocations__address')
            address = ', '.join([div.get_text(strip=True) for div in address_divs])
            addresses.append(address)
            print(f"Address => {address}")
        except:
            addresses.append("null")
        try:
            provider_number_div = soup.find_all('div', class_='ProviderDetailsLocations__phone')
            provider_number = ', '.join([div.get_text(strip=True) for div in provider_number_div])
            provider_numbers.append(provider_number)
            print(f"Provider number => {provider_number}")
        except:
            provider_numbers.append("null")
            
        try:
            patient_rating = soup.find('div', class_='ProviderDetailsRatings__simple-patient-survey-rating-row').find('span', class_='StarRating StarRating__can-focus').get('aria-label')
            patient_survey_ratings.append(patient_rating)
        except:
            patient_survey_ratings.append('null')
            
        try:
            hospital_rating = soup.find('div', class_='ProviderDetailsRatings__simple-overall-rating-row').find('span', class_='StarRating StarRating__can-focus').get('aria-label')
            hospital_ratings.append(hospital_rating)
        except:
            hospital_ratings.append('null')

        print("----------------------------------------------------------")
        i += 1

    print(f"Length of Arrays:")
    print(f"Names: {len(names)}")
    print(f"Addresses: {len(addresses)}")
    print(f"Provider Numbers: {len(provider_numbers)}")
    print(f"Qualities: {len(qualities)}")
    print(f"Hospital Types: {len(hospital_types)}")
    print(f"Emergency Services: {len(emergency_services)}")
    print(f"URLs: {len(urls)}")
    print("----------------------------------------------------------")

    # Create a pandas DataFrame
    data = {
        'name': names,
        'address': addresses,
        'providerNumber': provider_numbers,
        'zipcode': zipcode,
        'qualities': qualities,
        'hospitalTypes': hospital_types,
        'emergencyServices': emergency_services,
        'urls': urls
    }

    return data


def get_plan_urls(plan_type,driver):
    plan_urls = []

    i = 1

    while True:
        time.sleep(3)
        if plan_type == 0:
            print(f"Plan Type => {plan_type}")
            plan_rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'm-c-card.PlanCard.PLAN_TYPE_MAPD'))
            )

        elif plan_type == 1:
            print(f"Plan Type => {plan_type}")
            plan_rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'm-c-card.PlanCard.PLAN_TYPE_PDP'))
            )

        elif plan_type == 2:
            print(f"Plan Type => {plan_type}")
            plan_rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'm-c-card.MedigapPlanCard.e2e-medigap-plan-card'))
            )

        for row in plan_rows:
            # Get PLAN URLs
            url = row.find_element(By.XPATH, './/a[text()="Plan Details"]').get_attribute('href')
            print(f"Plan URL => {url}")
            plan_urls.append(url)

        try:
            next_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'ds-c-button.ds-c-button--ghost.Pagination__navButton.Pagination__next'))
            )
            next_button.click()
            print(f"Page {i} completed")
        except Exception as e:
            print(f"All {i} Pages Done!!!")
            break
        i += 1

    return plan_urls


def get_data_from_table(soup, text__):
    soup.find('th', text=text__).find_next_sibling('td').text.strip()


def get_multiple_line_text(soup, text__):
    soup.find("th", text=text__).find_next_sibling("td").get_text(separator=' ')


def plan_comparison(zipcode):
    plan_names = []
    plan_types = []
    plan_ids = []
    plans_urls = []
    planwebsitelink =[]
    non_members_numbers = []
    members_numbers = []
    total_monthly_premiums = []
    health_premiums = []
    drug_premiums = []
    standard_part_b_premiums = []
    part_b_premium_reductions = []
    health_deductibles = []
    drug_deductibles = []
    maximum_pay_for_health_services = []
    plan_addresses = []
    primary_doctor_visits = []
    specialists_visits = []
    diagnostics_test_and_procedures = []
    lab_services = []
    diagnostic_radiology_services = []
    outpatient_xrays = []
    emergency_cares = []
    urgent_cares = []
    inpatient_hospital_coverages = []
    outpatient_hospital_coverages = []
    skilled_nursing_facilities = []
    preventive_services = []
    ground_ambulances = []
    occupational_therapy_visits = []
    physical_therapy_and_speech_and_language_therapy_visits = []
    tier_1s = []
    tier_1_initial_coverage_phases = []
    tier_1_gap_coverage_phases = []
    tier_1_catastrophic_coverage_phases = []
    tier_2s = []
    tier_2_initial_coverage_phases = []
    tier_2_gap_coverage_phases = []
    tier_2_catastrophic_coverage_phases = []
    tier_3s = []
    tier_3_initial_coverage_phases = []
    tier_3_gap_coverage_phases = []
    tier_3_catastrophic_coverage_phases = []
    tier_4s = []
    tier_4_initial_coverage_phases = []
    tier_4_gap_coverage_phases = []
    tier_4_catastrophic_coverage_phases = []
    tier_5s = []
    tier_5_initial_coverage_phases = []
    tier_5_gap_coverage_phases = []
    tier_5_catastrophic_coverage_phases = []
    tier_6s = []
    tier_6_initial_coverage_phases = []
    tier_6_gap_coverage_phases = []
    tier_6_catastrophic_coverage_phases = []
    chemotherapy_drugs = []
    other_part_b_drugs = []
    part_b_insulins = []
    hearing_exams = []
    fitting_or_evaluations = []
    hearing_aids = []
    oral_exams = []
    cleanings = []
    fluoride_treatments = []
    dental_x_rays = []
    non_routine_services = []
    diagnostic_services = []
    restorative_services = []
    endodontics = []
    periodontics = []
    extractions = []
    prosthodontics_and_other_services = []
    routine_eye_exams = []
    contact_lenses = []
    eyeglasses = []
    eyeglasses_frames_only = []
    eyeglasses_lenses_only = []
    upgrades = []
    # options = Options()
    # options.add_argument('--headless')  # Run Chrome in headless mode
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Start the WebDriver with the Service and options
    # driver = uc.Chrome()
    driver.set_window_size(928, 1032)
    # for plan_type_n in range(0, 2):
    url = "https://www.medicare.gov/plan-compare/#/?year=2024&lang=en"

    driver.get(url)

    zip_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ds-c-field'))
    )

    zip_element.clear()
    time.sleep(1.5)
    zip_element.send_keys(zipcode)
    time.sleep(1.5)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "ds-c-button.ds-c-button--solid.mct-c-coverage-selector-v2__start-button"))
    ).click()

    try:
        plan_types_radio = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ds-c-choice'))
        )
    except:
        print("No Plan Types Found")
        # Create a dictionary that maps each category to its corresponding list
        data = {
            "Plan Name": "NULL",
            "Plan Type": "NULL",
            "Plan URL": "NULL",
            "Plan ID": "NULL",
            "Non-Members Number": "NULL",
            "Members Number": "NULL",
            "Total Monthly Premiums": "NULL",
            "Health Premiums": "NULL",
            "Drug Premiums": "NULL",
            "Standard Part B Premiums": "NULL",
            "Part B Premium Reductions": "NULL",
            "Health Deductibles": "NULL",
            "Drug Deductibles": "NULL",
            "Maximum Pay for Health Services": "NULL",
            "Plan Addresses": "NULL",
            "Primary Doctor Visits": "NULL",
            "Specialists Visits": "NULL",
            "Diagnostics Test and Procedures": "NULL",
            "Lab Services": "NULL",
            "Diagnostic Radiology Services": "NULL",
            "Outpatient X-rays": "NULL",
            "Emergency Cares": "NULL",
            "Urgent Cares": "NULL",
            "Inpatient Hospital Coverages": "NULL",
            "Outpatient Hospital Coverages": "NULL",
            "Skilled Nursing Facilities": "NULL",
            "Preventive Services": "NULL",
            "Ground Ambulances": "NULL",
            "Occupational Therapy Visits": "NULL",
            "Physical Therapy and Speech and Language Therapy Visits": "NULL",
            "Tier 1": "NULL",
            "Tier 1 Initial Coverage Phases": "NULL",
            "Tier 1 Gap Coverage Phases": "NULL",
            "Tier 1 Catastrophic Coverage Phases": "NULL",
            "Tier 2": "NULL",
            "Tier 2 Initial Coverage Phases": "NULL",
            "Tier 2 Gap Coverage Phases": "NULL",
            "Tier 2 Catastrophic Coverage Phases": "NULL",
            "Tier 3": "NULL",
            "Tier 3 Initial Coverage Phases": "NULL",
            "Tier 3 Gap Coverage Phases": "NULL",
            "Tier 3 Catastrophic Coverage Phases": "NULL",
            "Tier 4": "NULL",
            "Tier 4 Initial Coverage Phases": "NULL",
            "Tier 4 Gap Coverage Phases": "NULL",
            "Tier 4 Catastrophic Coverage Phases": "NULL",
            "Tier 5": "NULL",
            "Tier 5 Initial Coverage Phases": "NULL",
            "Tier 5 Gap Coverage Phases": "NULL",
            "Tier 5 Catastrophic Coverage Phases": "NULL",
            "Tier 6": "NULL",
            "Tier 6 Initial Coverage Phases": "NULL",
            "Tier 6 Gap Coverage Phases": "NULL",
            "Tier 6 Catastrophic Coverage Phases": "NULL",
            "Chemotherapy Drugs": "NULL",
            "Other Part B Drugs": "NULL",
            "Part B Insulins": "NULL",
            "Hearing Exams": "NULL",
            "Fitting or Evaluations": "NULL",
            "Hearing Aids": "NULL",
            "Oral Exams": "NULL",
            "Cleanings": "NULL",
            "Fluoride Treatments": "NULL",
            "Dental X-rays": "NULL",
            "Non-routine Services": "NULL",
            "Diagnostic Services": "NULL",
            "Restorative Services": "NULL",
            "Endodontics": "NULL",
            "Periodontics": "NULL",
            "Extractions": "NULL",
            "Prosthodontics and Other Services": "NULL",
            "Routine Eye Exams": "NULL",
            "Contact Lenses": "NULL",
            "Eyeglasses": "NULL",
            "Eyeglasses Frames Only": "NULL",
            "Eyeglasses Lenses Only": "NULL",
            "Upgrades": "NULL"
        }
        return data

    time.sleep(1.5)

    plan_types_radio[1].click() # 0 For 1st Plan

    time.sleep(1.5)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'ds-c-button.ds-c-button--solid.mct-c-coverage-selector-v2__start-button')
        )
    ).click()

    # if plan_type_n <= 1:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//span[text()="I\'m not sure"]/parent::*/preceding-sibling::*'))
    ).click()
    time.sleep(.5)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Continue Without Logging In"]'))
    ).click()
    radio_buttons = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'ds-c-choice'))
    )
    radio_buttons[1].click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Next"]'))
    ).click()
    time.sleep(2)

    plan_urls_current = get_plan_urls(1 ,driver)

    i = 1

    for url__ in plan_urls_current:
        print(f"For Plan Type ({1}) | {i}/{len(plan_urls_current)} | url: {url__}")
        driver.get(url__)

        driver.refresh()

        plans_urls.append(url__)

        time.sleep(0.5)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "plan-contact"))
            )   
        except:
            time.sleep(2)
            # pass
        try:
            plan_website_link = driver.find_element(By.ID, "plan-contact").get_attribute("href")
            
            planwebsitelink.append(plan_website_link)
        except:
            planwebsitelink.append("not found")
            
        time.sleep(0.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        # pprint(soup)

        # PLAN NAME!
        try:
            plan_name = soup.find('h1', class_="e2e-plan-details-plan-header").text.strip()
            print(f"Plan Name: {plan_name}")
            plan_names.append(plan_name)
        except:
            plan_names.append("null")

        # PLAN TYPE!
        try:
            plan_type = soup.find('span',
                                    class_="PlanDetailsPagePlanInfo__value e2e-plan-details-plan-type").text.strip()
            print(f"Plan Type: {plan_type}")
            plan_types.append(plan_type)
        except:
            plan_types.append("null")

        # PLAN ID!
        try:
            plan_id = soup.find("span", string="Plan ID:").find_next_sibling('span').text.strip()
            print(f"Plan ID: {plan_id}")
            plan_ids.append(plan_id)
        except:
            plan_ids.append("null")

        # NON-MEMBERS PHONE NUMBER!
        try:
            non_member_number = soup.find("a", id="non-members-number").text.strip()
            print(f"Non Member Number: {non_member_number}")
            non_members_numbers.append(non_member_number)
        except:
            non_members_numbers.append("null")

        # MEMBERS PHONE NUMBER
        try:
            member_phone_number = soup.find("a", id="members-number").text.strip()
            print(f"Member Phone Number: {member_phone_number}")
            members_numbers.append(member_phone_number)
        except:
            members_numbers.append("null")

        # TOTAL MONTHLY PREMIUM!
        try:
            total_monthly_premium = soup.find("th", string="Total monthly premium").find_next_sibling(
                "td").get_text(separator=' ')
            print(f"Total Monthly Premium: {total_monthly_premium}")
            total_monthly_premiums.append(total_monthly_premium)
        except:
            total_monthly_premiums.append("null")

        # HEALTH PREMIUM!
        try:
            health_premium = soup.find("th", string="Health premium").find_next_sibling("td").get_text()
            print(f"Health Premium: {health_premium}")
            health_premiums.append(health_premium)
        except:
            health_premiums.append("null")

        # DRUG PREMIUM!
        try:
            drug_premium = soup.find("th", string="Drug premium").find_next_sibling("td").get_text()
            print(f"Drug Premium: {drug_premium}")
            drug_premiums.append(drug_premium)
        except:
            drug_premiums.append("null")

        # Standard Part B Premium!
        try:
            standard_part_b_premium = soup.find("th", string="Standard Part B premium").find_next_sibling(
                "td").get_text(separator=' ')
            print(f"Standard Part B Premium: {standard_part_b_premium}")
            standard_part_b_premiums.append(standard_part_b_premium)
        except:
            standard_part_b_premiums.append("null")

        # Part B premium reduction
        try:
            part_b_premium_reduction = soup.find("th", string="Part B premium reduction").find_next_sibling(
                "td").get_text(separator=' ')
            print(f"Part B Premium Reduction: {part_b_premium_reduction}")
            part_b_premium_reductions.append(part_b_premium_reduction)
        except:
            part_b_premium_reductions.append("null")

        # Health Deductible!
        try:
            health_ded = soup.find("th", string="Health deductible").find_next_sibling("td").get_text(
                separator=' ')
            print(f"Health Deductible: {health_ded}")
            health_deductibles.append(health_ded)
        except:
            health_deductibles.append("null")

        # Drug deductible
        try:
            drug_ded = soup.find("th", string="Drug deductible").find_next_sibling("td").get_text(separator=' ')
            print(f"Drug Deductible: {drug_ded}")
            drug_deductibles.append(drug_ded)
        except:
            drug_deductibles.append("null")

        # Maximum you pay for health services
        try:
            max_pay_for_health_service = soup.find('span',
                                                    string='Maximum you pay for health services').find_parent(
                'th').find_next_sibling('td').get_text()
            print(f"Max Pay For Health Service: {max_pay_for_health_service}")
            maximum_pay_for_health_services.append(max_pay_for_health_service)
        except:
            maximum_pay_for_health_services.append("null")

        # Address
        try:
            address_element = soup.find('address', class_='ds-u-font-style--normal').get_text(separator=' ')
            print(f"Address: {address_element}")
            plan_addresses.append(address_element)
        except:
            plan_addresses.append("null")

        # Primary doctor visit
        try:
            primary_doctor_visit = soup.find("th", string="Primary doctor visit").find_next_sibling(
                "td").get_text(separator=' ')
            print(f"Primary Doctor Visit: {primary_doctor_visit}")
            primary_doctor_visits.append(primary_doctor_visit)
        except:
            primary_doctor_visits.append("null")

        # Specialist visit
        try:
            specialist_visit = soup.find('th', string='Specialist visit').find_next_sibling('td').get_text(
                separator=' ')
            print(f"Specialist Visit: {specialist_visit}")
            specialists_visits.append(specialist_visit)
        except:
            specialists_visits.append("null")

        # Diagnostic tests & procedures
        try:
            diagnostic_tests_procedure = soup.find('span', string='Diagnostic tests & procedures').find_parent(
                'th').find_next_sibling('td').get_text(separator=' ')
            print(f"Diagnostic Tests & Procedures: {diagnostic_tests_procedure}")
            diagnostics_test_and_procedures.append(diagnostic_tests_procedure)
        except:
            diagnostics_test_and_procedures.append("null")

        # Lab services
        try:
            lab_service = soup.find('th', string='Lab services').find_next_sibling('td').get_text(separator=' ')
            print(f"Lab Services: {lab_service}")
            lab_services.append(lab_service)
        except:
            lab_services.append("null")

        # Diagnostic radiology services (like MRI)
        try:
            diagnostic_radiology_service = soup.find('th',
                                                        string='Diagnostic radiology services (like MRI)').find_next_sibling(
                'td').get_text(separator=' ')
            print(f"Diagnostic Radiology Services: {diagnostic_radiology_service}")
            diagnostic_radiology_services.append(diagnostic_radiology_service)
        except:
            diagnostic_radiology_services.append("null")

        # Outpatient x-rays
        try:
            outpatient_xray = soup.find('th', string='Outpatient x-rays').find_next_sibling('td').get_text(
                separator=' ')
            print(f"Outpatient X-Rays: {outpatient_xray}")
            outpatient_xrays.append(outpatient_xray)
        except:
            outpatient_xrays.append("null")

        # Emergency care
        try:
            emergency_care = soup.find('th', string='Emergency care').find_next_sibling('td').get_text(
                separator=' ')
            print(f"Emergency Care: {emergency_care}")
            emergency_cares.append(emergency_care)
        except:
            emergency_cares.append("null")

        # Urgent care
        try:
            urgent_care = soup.find('th', string='Urgent care').find_next_sibling('td').get_text(separator=' ')
            print(f"Urgent Care: {urgent_care}")
            urgent_cares.append(urgent_care)
        except:
            urgent_cares.append("null")

        # Inpatient hospital coverage
        try:
            inpatient_hospital_coverage = soup.find('th',
                                                    string='Inpatient hospital coverage').find_next_sibling(
                'td').get_text(separator=' ')
            print(f"Inpatient Hospital Coverage: {inpatient_hospital_coverage}")
            inpatient_hospital_coverages.append(inpatient_hospital_coverage)
        except:
            inpatient_hospital_coverages.append("null")

        # Outpatient hospital coverage
        try:
            outpatient_hospital_coverage = soup.find('th',
                                                        string='Outpatient hospital coverage').find_next_sibling(
                'td').get_text(separator=' ')
            print(f"Outpatient Hospital Coverage: {outpatient_hospital_coverage}")
            outpatient_hospital_coverages.append(outpatient_hospital_coverage)
        except:
            outpatient_hospital_coverages.append("null")

        # Skilled nursing facility
        try:
            skilled_nursing_facility = soup.find('th', string='Skilled nursing facility').find_next_sibling(
                'td').get_text(separator=' ')
            print(f"Skilled Nursing Facility: {skilled_nursing_facility}")
            skilled_nursing_facilities.append(skilled_nursing_facility)
        except:
            skilled_nursing_facilities.append("null")

        # Preventive services
        try:
            preventive_service = soup.find('th', string='Preventive services').find_next_sibling('td').get_text(
                separator=' ')
            print(f"Preventive Services: {preventive_service}")
            preventive_services.append(preventive_service)
        except:
            preventive_services.append("null")

        # Ground ambulance
        try:
            ground_ambulance = soup.find('th', string='Ground ambulance').find_next_sibling('td').get_text(
                separator=' ')
            print(f"Ground Ambulance: {ground_ambulance}")
            ground_ambulances.append(ground_ambulance)
        except:
            ground_ambulances.append("null")

        # Occupational therapy visit
        try:
            occupational_therapy_visit = soup.find('th', string='Occupational therapy visit').find_next_sibling(
                'td').get_text(separator=' ')
            print(f"Occupational Therapy Visit: {occupational_therapy_visit}")
            occupational_therapy_visits.append(occupational_therapy_visit)
        except:
            occupational_therapy_visits.append("null")

        # Physical therapy & speech & language therapy visit
        try:
            physical_therapy_speech_language_therapy_visit = soup.find('th',
                                                                        string='Physical therapy & speech & language therapy visit').find_next_sibling(
                'td').get_text(separator=' ')
            print(
                f"Physical Therapy & Speech & Language Therapy Visit: {physical_therapy_speech_language_therapy_visit}")
            physical_therapy_and_speech_and_language_therapy_visits.append(
                physical_therapy_speech_language_therapy_visit)
        except:
            physical_therapy_and_speech_and_language_therapy_visits.append("null")

        # -------------------------------------- TIERS START HERE --------------------------------------

        # Wait for the page to load completely (adjust the timeout as needed)
        wait = WebDriverWait(driver, 1)

        # Tier 1: Preferred Generic
        try:
            tier_1_preferred_generic = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Preferred Generic']"))).text
            print(f"Tier 1: {tier_1_preferred_generic}")
            tier_1s.append(tier_1_preferred_generic)
        except:
            tier_1s.append("null")

        # Tier 1s Initial coverage phase
        try:
            tier_1_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Preferred Generic']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"Tier 1 Initial Coverage Phase: {tier_1_initial_coverage_phase}")
            tier_1_initial_coverage_phases.append(tier_1_initial_coverage_phase)
        except:
            tier_1_initial_coverage_phases.append("null")

        # Ties 1s Gap coverage phase
        try:
            tier_1_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Preferred Generic']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"Tier 1 Gap Coverage Phase: {tier_1_gap_coverage_phase}")
            tier_1_gap_coverage_phases.append(tier_1_gap_coverage_phase)
        except:
            tier_1_gap_coverage_phases.append("null")

        # Tier 1s Catastrophic coverage phase
        try:
            tier_1_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Preferred Generic']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"Tier 1 Catastrophic Coverage Phase: {tier_1_catastrophic_coverage_phase}")
            tier_1_catastrophic_coverage_phases.append(tier_1_catastrophic_coverage_phase)
        except:
            tier_1_catastrophic_coverage_phases.append("null")

        # TIER 2 STARTS HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Tier 2: Generic
        try:
            tier_2_generic = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Generic']"))).text
            print(f"TIER 2: {tier_2_generic}")
            tier_2s.append(tier_2_generic)
        except:
            tier_2s.append("null")

        # Tier 2s Initial coverage phase
        try:
            tier_2_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Generic']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"Tier 2 Initial Coverage Phase: {tier_2_initial_coverage_phase}")
            tier_2_initial_coverage_phases.append(tier_2_initial_coverage_phase)
        except:
            tier_2_initial_coverage_phases.append("null")

        # Ties 2s Gap coverage phase
        try:
            tier_2_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Generic']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"Tier 2 Gap Coverage Phase: {tier_2_gap_coverage_phase}")
            tier_2_gap_coverage_phases.append(tier_2_gap_coverage_phase)
        except:
            tier_2_gap_coverage_phases.append("null")

        # Tier 2s Catastrophic coverage phase
        try:
            tier_2_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Generic']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"Tier 2 Catastrophic Coverage Phase: {tier_2_catastrophic_coverage_phase}")
            tier_2_catastrophic_coverage_phases.append(tier_2_catastrophic_coverage_phase)
        except:
            tier_2_catastrophic_coverage_phases.append("null")

        # TIER 3 STARTS HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Tier 3: Preferred Brand
        try:
            tier_3_preferred_brand = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Preferred Brand']"))).text
            print(f"Tier 3: {tier_3_preferred_brand}")
            tier_3s.append(tier_3_preferred_brand)
        except:
            tier_3s.append("null")

        # Tier 3s Initial coverage phase
        try:
            tier_3_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Preferred Brand']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"Tier 3 Initial Coverage Phase: {tier_3_initial_coverage_phase}")
            tier_3_initial_coverage_phases.append(tier_3_initial_coverage_phase)
        except:
            tier_3_initial_coverage_phases.append("null")

        # Ties 3s Gap coverage phase
        try:
            tier_3_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Preferred Brand']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"Tier 3 Gap Coverage Phase: {tier_3_gap_coverage_phase}")
            tier_3_gap_coverage_phases.append(tier_3_gap_coverage_phase)
        except:
            tier_3_gap_coverage_phases.append("null")

        # Tier 3s Catastrophic coverage phase
        try:
            tier_3_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Preferred Brand']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"Tier 3 Catastrophic Coverage Phase: {tier_3_catastrophic_coverage_phase}")
            tier_3_catastrophic_coverage_phases.append(tier_3_catastrophic_coverage_phase)
        except:
            tier_3_catastrophic_coverage_phases.append("null")

        # TIER 4 STARTS HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Tier 4s Non-Preferred Drug
        try:
            tier_4_non_preferred_drug = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Non-Preferred Drug']"))).text
            print(f"TIER 4: {tier_4_non_preferred_drug}")
            tier_4s.append(tier_4_non_preferred_drug)
        except:
            try:
                tier_4_non_preferred_drug = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//th[text()='Non-Preferred Brand']"))).text
                print(f"TIER 4: {tier_4_non_preferred_drug}")
                tier_4s.append(tier_4_non_preferred_drug)
            except:
                tier_4s.append("null")

        # Tier 4s Initial coverage phase
        try:
            tier_4_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Non-Preferred Drug']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"TIER 4 Initial Coverage Phase: {tier_4_initial_coverage_phase}")
            tier_4_initial_coverage_phases.append(tier_4_initial_coverage_phase)
        except:
            try:
                tier_4_initial_coverage_phase = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//th[text()='Non-Preferred Brand']/following-sibling::td"))
                ).find_element(By.TAG_NAME, "div").text
                print(f"TIER 4 Initial Coverage Phase: {tier_4_initial_coverage_phase}")
                tier_4_initial_coverage_phases.append(tier_4_initial_coverage_phase)
            except:
                tier_4_initial_coverage_phases.append("null")

        # Ties 4s Gap coverage phase
        try:
            tier_4_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Non-Preferred Drug']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"TIER 4 Gap Coverage Phase: {tier_4_gap_coverage_phase}")
            tier_4_gap_coverage_phases.append(tier_4_gap_coverage_phase)
        except:
            try:
                tier_4_gap_coverage_phase = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//th[text()='Non-Preferred Brand']/following-sibling::td"))
                )[1].text.replace("\n", " ")
                print(f"TIER 4 Gap Coverage Phase: {tier_4_gap_coverage_phase}")
                tier_4_gap_coverage_phases.append(tier_4_gap_coverage_phase)
            except:
                tier_4_gap_coverage_phases.append("null")

        # Tier 4s Catastrophic coverage phase
        try:
            tier_4_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Non-Preferred Drug']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"TIER 4 Catastrophic Coverage Phase: {tier_4_catastrophic_coverage_phase}")
            tier_4_catastrophic_coverage_phases.append(tier_4_catastrophic_coverage_phase)
        except:
            try:
                tier_4_catastrophic_coverage_phase = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//th[text()='Non-Preferred Brand']/following-sibling::td"))
                )[2].text.replace("\n", " ")
                print(f"TIER 4 Catastrophic Coverage Phase: {tier_4_catastrophic_coverage_phase}")
                tier_4_catastrophic_coverage_phases.append(tier_4_catastrophic_coverage_phase)
            except:
                tier_4_catastrophic_coverage_phases.append("null")

        # TIER 5 STARTS HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Tier 5s Specialty Tier
        try:
            tier_5_speciality_tier = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Specialty Tier']"))).text
            print(f"TIER 5: {tier_5_speciality_tier}")
            tier_5s.append(tier_5_speciality_tier)
        except:
            tier_5s.append("null")

        # Tier 5s Initial coverage phase
        try:
            tier_5_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Specialty Tier']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"Tier 5s Initial Coverage Phase: {tier_5_initial_coverage_phase}")
            tier_5_initial_coverage_phases.append(tier_5_initial_coverage_phase)
        except:
            tier_5_initial_coverage_phases.append("null")

        # Ties 5s Gap coverage phase
        try:
            tier_5_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Specialty Tier']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"Tier 5s Gap Coverage Phase: {tier_5_gap_coverage_phase}")
            tier_5_gap_coverage_phases.append(tier_5_gap_coverage_phase)
        except:
            tier_5_gap_coverage_phases.append("null")

        # Tier 5s Catastrophic coverage phase
        try:
            tier_5_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Specialty Tier']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"Tier 5s Catastrophic Coverage Phase: {tier_5_catastrophic_coverage_phase}")
            tier_5_catastrophic_coverage_phases.append(tier_5_catastrophic_coverage_phase)
        except:
            tier_5_catastrophic_coverage_phases.append("null")

        # TIER 6 STARTS HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Tier 6s Select Care Drugs
        try:
            tier_6_select_care_drugs = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Select Care Drugs']"))).text
            print(f"TIER 6: {tier_6_select_care_drugs}")
            tier_6s.append(tier_6_select_care_drugs)
        except:
            tier_6s.append("null")

        # Tier 6s Initial coverage phase
        try:
            tier_6_initial_coverage_phase = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//th[text()='Select Care Drugs']/following-sibling::td"))
            ).find_element(By.TAG_NAME, "div").text
            print(f"TIER 6 Initial Coverage Phase: {tier_6_initial_coverage_phase}")
            tier_6_initial_coverage_phases.append(tier_6_initial_coverage_phase)
        except:
            tier_6_initial_coverage_phases.append("null")

        # Ties 6s Gap coverage phase
        try:
            tier_6_gap_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Select Care Drugs']/following-sibling::td"))
            )[1].text.replace("\n", " ")
            print(f"TIER 6 Gap Coverage Phase: {tier_6_gap_coverage_phase}")
            tier_6_gap_coverage_phases.append(tier_6_gap_coverage_phase)
        except:
            tier_6_gap_coverage_phases.append("null")

        # Tier 6s Catastrophic coverage phase
        try:
            tier_6_catastrophic_coverage_phase = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//th[text()='Select Care Drugs']/following-sibling::td"))
            )[2].text.replace("\n", " ")
            print(f"TIER 6 Catastrophic Coverage Phase: {tier_6_catastrophic_coverage_phase}")
            tier_6_catastrophic_coverage_phases.append(tier_6_catastrophic_coverage_phase)
        except:
            tier_6_catastrophic_coverage_phases.append("null")

        # -------------------------------------TIERS END HERE------------------------------------------

        # CHEMOTHERAPY DRUGS
        try:
            chemotherapy_drug = soup.find("th", string="Chemotherapy drugs").find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Chemotherapy Drug: {chemotherapy_drug}")
            chemotherapy_drugs.append(chemotherapy_drug)
        except:
            chemotherapy_drugs.append("null")

        # Other Part B drugs
        try:
            other_part_b_drug = soup.find('th', string='Other Part B drugs').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Other Part B Drug: {other_part_b_drug}")
            other_part_b_drugs.append(other_part_b_drug)
        except:
            other_part_b_drugs.append("null")

        # Part B insulin
        try:
            part_b_insulin = soup.find('th', string='Part B insulin').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Part B Insulin: {part_b_insulin}")
            part_b_insulins.append(part_b_insulin)
        except:
            part_b_insulins.append("null")

        # Hearing exam
        try:
            hearing_exam = soup.find('th', string='Hearing exam').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Hearing Exam: {hearing_exam}")
            hearing_exams.append(hearing_exam)
        except:
            hearing_exams.append("null")

        # Fitting/evaluation
        try:
            fitting_evaluation = soup.find('th', string='Fitting/evaluation').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Fitting/Evaluation: {fitting_evaluation}")
            fitting_or_evaluations.append(fitting_evaluation)
        except:
            fitting_or_evaluations.append("null")

        # Hearing aids - all types
        try:
            hearing_aid = soup.find('th', string='Hearing aids - all types').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Hearing Aids: {hearing_aid}")
            hearing_aids.append(hearing_aid)
        except:
            hearing_aids.append("null")

        # Oral exam
        try:
            oral_exam = soup.find('th', string='Oral exam').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Oral Exam: {oral_exam}")
            oral_exams.append(oral_exam)
        except:
            oral_exams.append("null")

        # Cleaning
        try:
            cleaning = soup.find('th', string='Cleaning').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Cleaning: {cleaning}")
            cleanings.append(cleaning)
        except:
            cleanings.append("null")

        # Fluoride treatment
        try:
            flouride_treatment = soup.find('th', string='Fluoride treatment').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Fluoride Treatment: {flouride_treatment}")
            fluoride_treatments.append(flouride_treatment)
        except:
            fluoride_treatments.append("null")

        # Dental x-rays
        try:
            dental_xray = soup.find('th', string='Dental x-rays').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Dental X-Rays: {dental_xray}")
            dental_x_rays.append(dental_xray)
        except:
            dental_x_rays.append("null")

        # Non-routine services
        try:
            non_routine_service = soup.find('th', string='Non-routine services').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Non-Routine Services: {non_routine_service}")
            non_routine_services.append(non_routine_service)
        except:
            non_routine_services.append("null")

        # Diagnostic services
        try:
            diagnostic_service = soup.find('th', string='Diagnostic services').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Diagnostic Services: {diagnostic_service}")
            diagnostic_services.append(diagnostic_service)
        except:
            diagnostic_services.append("null")

        # Restorative services
        try:
            restorative_service = soup.find('th', string='Restorative services').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Restorative Services: {restorative_service}")
            restorative_services.append(restorative_service)
        except:
            restorative_services.append("null")

        # Endodontics
        try:
            endodontic = soup.find('th', string='Endodontics').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Endodontics: {endodontic}")
            endodontics.append(endodontic)
        except:
            endodontics.append("null")

        # Periodontics
        try:
            periodontic = soup.find('th', string='Periodontics').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Periodontics: {periodontic}")
            periodontics.append(periodontic)
        except:
            periodontics.append("null")

        # Extractions
        try:
            extraction = soup.find('th', string='Extractions').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Extractions: {extraction}")
            extractions.append(extraction)
        except:
            extractions.append("null")

        # Prosthodontics, other oral/maxillofacial surgery, & other services
        try:
            prosthodontics = soup.find('th',
                                        string='Prosthodontics, other oral/maxillofacial surgery, & other services').find_next_sibling(
                'td').find('div').get_text(separator=' ')
            print(f"Prosthodontics: {prosthodontics}")
            prosthodontics_and_other_services.append(prosthodontics)
        except:
            prosthodontics_and_other_services.append("null")

        # Routine eye exam
        try:
            routine_eye_exam = soup.find('th', string='Routine eye exam').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Routine Eye Exam: {routine_eye_exam}")
            routine_eye_exams.append(routine_eye_exam)
        except:
            routine_eye_exams.append("null")

        # Contact lenses
        try:
            contact_lense = soup.find('th', string='Contact lenses').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Contact Lenses: {contact_lense}")
            contact_lenses.append(contact_lense)
        except:
            contact_lenses.append("null")

        # Eyeglasses (frames & lenses)
        try:
            eyeglasse = soup.find('th', string='Eyeglasses (frames & lenses)').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Eyeglasses: {eyeglasse}")
            eyeglasses.append(eyeglasse)
        except:
            eyeglasses.append("null")

        # Eyeglass frames only
        try:
            frames_only = soup.find('th', string='Eyeglass frames only').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Eyeglass frames only: {frames_only}")
            eyeglasses_frames_only.append(frames_only)
        except:
            eyeglasses_frames_only.append("null")

        # Eyeglass lenses only
        try:
            eyeglass_lense_only = soup.find('th', string='Eyeglass lenses only').find_next_sibling('td').find(
                'div').get_text(separator=' ')
            print(f"Eyeglass lenses only: {eyeglass_lense_only}")
            eyeglasses_lenses_only.append(eyeglass_lense_only)
        except:
            eyeglasses_lenses_only.append("null")

        # Upgrades
        try:
            upgrade = soup.find('th', string='Upgrades').find_next_sibling('td').find('div').get_text(
                separator=' ')
            print(f"Upgrades: {upgrade}")
            upgrades.append(upgrade)
        except:
            upgrades.append("null")

        print("----------------------------------------------------")

        i+=1

    pprint(plans_urls)
    print("\n\n\nplan len ===>>>>> I'm here",len(plans_urls))

    # GET DATA FROM PLAN URLS!!!

    # if plan_type_n == 2:
    #     # DIFFERENT STRUCTURE AND QUESTIONS!!!
    #     print(plan_type_n)

    # Create a dictionary that maps each category to its corresponding list
    data = {
        "Plan Name": plan_names,
        "Plan Type": plan_types,
        "Plan URL": plans_urls,
        "Plan ID": plan_ids,
        "Non-Members Number": non_members_numbers,
        "Members Number": members_numbers,
        "Total Monthly Premiums": total_monthly_premiums,
        "Health Premiums": health_premiums,
        "Drug Premiums": drug_premiums,
        "Standard Part B Premiums": standard_part_b_premiums,
        "Part B Premium Reductions": part_b_premium_reductions,
        "Health Deductibles": health_deductibles,
        "Drug Deductibles": drug_deductibles,
        "Maximum Pay for Health Services": maximum_pay_for_health_services,
        "Plan Addresses": plan_addresses,
        "Primary Doctor Visits": primary_doctor_visits,
        "Specialists Visits": specialists_visits,
        "Diagnostics Test and Procedures": diagnostics_test_and_procedures,
        "Lab Services": lab_services,
        "Diagnostic Radiology Services": diagnostic_radiology_services,
        "Outpatient X-rays": outpatient_xrays,
        "Emergency Cares": emergency_cares,
        "Urgent Cares": urgent_cares,
        "Inpatient Hospital Coverages": inpatient_hospital_coverages,
        "Outpatient Hospital Coverages": outpatient_hospital_coverages,
        "Skilled Nursing Facilities": skilled_nursing_facilities,
        "Preventive Services": preventive_services,
        "Ground Ambulances": ground_ambulances,
        "Occupational Therapy Visits": occupational_therapy_visits,
        "Physical Therapy and Speech and Language Therapy Visits": physical_therapy_and_speech_and_language_therapy_visits,
        "Tier 1": tier_1s,
        "Tier 1 Initial Coverage Phases": tier_1_initial_coverage_phases,
        "Tier 1 Gap Coverage Phases": tier_1_gap_coverage_phases,
        "Tier 1 Catastrophic Coverage Phases": tier_1_catastrophic_coverage_phases,
        "Tier 2": tier_2s,
        "Tier 2 Initial Coverage Phases": tier_2_initial_coverage_phases,
        "Tier 2 Gap Coverage Phases": tier_2_gap_coverage_phases,
        "Tier 2 Catastrophic Coverage Phases": tier_2_catastrophic_coverage_phases,
        "Tier 3": tier_3s,
        "Tier 3 Initial Coverage Phases": tier_3_initial_coverage_phases,
        "Tier 3 Gap Coverage Phases": tier_3_gap_coverage_phases,
        "Tier 3 Catastrophic Coverage Phases": tier_3_catastrophic_coverage_phases,
        "Tier 4": tier_4s,
        "Tier 4 Initial Coverage Phases": tier_4_initial_coverage_phases,
        "Tier 4 Gap Coverage Phases": tier_4_gap_coverage_phases,
        "Tier 4 Catastrophic Coverage Phases": tier_4_catastrophic_coverage_phases,
        "Tier 5": tier_5s,
        "Tier 5 Initial Coverage Phases": tier_5_initial_coverage_phases,
        "Tier 5 Gap Coverage Phases": tier_5_gap_coverage_phases,
        "Tier 5 Catastrophic Coverage Phases": tier_5_catastrophic_coverage_phases,
        "Tier 6": tier_6s,
        "Tier 6 Initial Coverage Phases": tier_6_initial_coverage_phases,
        "Tier 6 Gap Coverage Phases": tier_6_gap_coverage_phases,
        "Tier 6 Catastrophic Coverage Phases": tier_6_catastrophic_coverage_phases,
        "Chemotherapy Drugs": chemotherapy_drugs,
        "Other Part B Drugs": other_part_b_drugs,
        "Part B Insulins": part_b_insulins,
        "Hearing Exams": hearing_exams,
        "Fitting or Evaluations": fitting_or_evaluations,
        "Hearing Aids": hearing_aids,
        "Oral Exams": oral_exams,
        "Cleanings": cleanings,
        "Fluoride Treatments": fluoride_treatments,
        "Dental X-rays": dental_x_rays,
        "Non-routine Services": non_routine_services,
        "Diagnostic Services": diagnostic_services,
        "Restorative Services": restorative_services,
        "Endodontics": endodontics,
        "Periodontics": periodontics,
        "Extractions": extractions,
        "Prosthodontics and Other Services": prosthodontics_and_other_services,
        "Routine Eye Exams": routine_eye_exams,
        "Contact Lenses": contact_lenses,
        "Eyeglasses": eyeglasses,
        "Eyeglasses Frames Only": eyeglasses_frames_only,
        "Eyeglasses Lenses Only": eyeglasses_lenses_only,
        "Upgrades": upgrades
    }

    # Iterate through each key-value pair in the data dictionary
    for key, value in data.items():
        # Calculate the length of the list
        length = len(value)
        # Print the key and the length of the list
        print(f"The length of '{key}' list is: {length}")

    # df = pd.DataFrame(data)
    # # Write the DataFrame to a CSV file
    # df.to_csv(f"provider_data_plan_comparison_{zipcode}.csv", index=False)
    driver.quit()
    
    return data

        
if __name__ == "__main__":
    # plan_comparison("33101")
    # List of zip codes to process
    zipcodes = [
        "33101", "33125", "33126", "33127", "33128", "33129", "33130", "33131", "33132", "33133",
        "32801", "32803", "32804", "32805", "32806", "32807", "32808", "32809", "32810", "32811",
        "33601", "33602", "33603", "33604", "33605", "33606", "33607", "33608", "33609", "33610",
        "32099", "32201", "32202", "32203", "32204", "32205", "32206", "32207", "32208", "32209",
        "00901", "00902", "00907", "00908", "00909", "00910", "00911", "00912", "00913", "00914",
        "00716", "00717", "00728", "00730", "00731", "00732", "00733", "00680", "00681", "00682",
        "00612", "00613", "00614"
    ]
    
    # zipcodes = [
    #     '33128'
    # ]
    
    def process_zipcode(zipcode):
        # driver = set_driver()
        try:
        #    data = plan_comparison(zipcode)
           
        #    print(f"Data for Zipcode: {zipcode}")
        #    pprint(data)
           
        #    # Iterate through each key-value pair in the data dictionary
        #    for key, value in data.items():
        #        # Calculate the length of the list
        #        length = len(value)
        #        # Print the key and the length of the list
        #        print(f"The length of '{key}' list is: {length}")

        #    df = pd.DataFrame(data)
        #    # Write the DataFrame to a CSV file
        #    df.to_csv(f"provider_data_plan_comparison_1_{zipcode}.csv", index=False)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
            ph_links = actions(driver, zipcode)
            
            print(ph_links)
            print(f"Total Links => {len(ph_links)}")
            ph_data = extract(driver, ph_links, zipcode)
            df = pd.DataFrame(ph_data)
            
            pprint(ph_data)
            # Write the DataFrame to a CSV file
            df.to_csv(f"provider_data_physicians_{zipcode}.csv", index=False)
            
        except:
            print(f"Error processing {zipcode}")
            
            ph_data = {
                'name': "NULL",
                'address_1':  "NULL",
                'address_2':  "NULL",
                'provider number 1':  "NULL",
                'provider number 2':  "NULL",
                'specialties':  "NULL",
                'consetion':  "NULL",
                'educations':  "NULL",
                'genders':  "NULL",
                'zipcode': zipcode,
                'url':  "NULL"
            }
            
            pprint(ph_data)
            df = pd.DataFrame(ph_data)
            # Write the DataFrame to a CSV file
            df.to_csv(f"provider_data_physicians_{zipcode}.csv", index=False) 
            
            driver.quit()
            
        # finally:
        #     driver.quit()
            
    threads = []
    for i in range(0, len(zipcodes), 4):
        for j in range(i, min(i + 4, len(zipcodes))):
            thread = threading.Thread(target=process_zipcode, args=(zipcodes[j],))
            threads.append(thread)
            thread.start()        
        
        for thread in threads:
            thread.join()
        threads = []

    # zipcode = "00962"

    # driver = set_driver()
    # plan_comparison(zipcode)

    # driver.quit()
    # For Hospitals
    # hosp_links = actions(driver, zipcode, mode='hospitals')
    # print(hosp_links)
    # print(f"Total Links => {len(hosp_links)}")
    # hosp_data = extract_hospitals(links, zipcode)
    # print(hosp_data)
    # print(len(hosp_data))

    # hosp_data_df = pd.DataFrame(hosp_data)

    # Write the DataFrame to a CSV file
    # csv_filename = f'provider_data_hospitals_{zipcode}.csv'
    # hosp_data_df.to_csv(csv_filename, index=False)
    # print(f"hosp_data_df saved to {csv_filename}")

    # For Physicians
    # ph_links = actions(driver, zipcode)
    # print(ph_links)
    # print(f"Total Links => {len(ph_links)}")
    # ph_data = extract_hospitals(links, zipcode)
    # print(ph_data)
    # print(len(ph_data))

    # ph_data_df = pd.DataFrame(pharma_data)

    # Write the DataFrame to a CSV file
    # csv_filename = f'provider_data_physicians_{zipcode}.csv'
    # ph_data_df.to_csv(csv_filename, index=False)
    # print(f"ph_data_df saved to {csv_filename}")

    # FOR PLAN Comparison
    # plan_comparison(zipcode)

    # driver.quit()

    # For Hospitals
    # links = actions(driver, zipcode, mode="hospitals")
    # print(links)
    # print(f"Total Links => {len(links)}")
