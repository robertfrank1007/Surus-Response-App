import os

from dotenv import load_dotenv

load_dotenv()

DATABRICKS_HOST = os.environ["DATABRICKS_HOST"]
DATABRICKS_HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]

VOTERFILE_TABLE = os.environ["VOTERFILE_TABLE"]
STAGING_TABLE = os.environ["STAGING_TABLE"]
PREDICTIONS_TABLE = os.environ["PREDICTIONS_TABLE"]

MODEL_URI = os.environ["MODEL_URI"]

# Column in VOTERFILE_TABLE that CSV external_ids match against
JOIN_KEY = "external_id"

# Voterfile columns used to derive age_days / reg_tenure_days
BIRTHDATE_COL = "birthdate"
REGISTERED_AT_COL = "registered_at"

# Feature columns the model was trained on, in the exact order/name it expects
FEATURE_COLS = [
    "sex",
    "ethnicity",
    "marital_status",
    "religion",
    "party",
    "occupation",
    "language",
    "custom_fields.education_level_score",
    "custom_fields.home_owner_score",
    "custom_fields.gun_owner_score",
    "custom_fields.presence_children_score",
    "custom_fields.cell_confidence_code",
    "custom_fields.estimated_home_value",
    "custom_fields.residence_families_hhcount",
    "custom_fields.residence_hhparties_description",
    "custom_fields.primary_voting_history",
    "custom_fields.turnout__likely_ev",
    "custom_fields.turnout__likely_vbm",
    "custom_fields.ideology_partisanship__primary_voter",
    "custom_fields.media__social_media_user",
    "custom_fields.behavior__candidate_mail_readership",
    "custom_fields.behavior__charity_giving_type",
    "custom_fields.behavior__most_important_policy_item",
    "custom_fields.behavior__church_attendance",
    "custom_fields.behavior__ticket_splitting",
    "custom_fields.behavior__ticket_splitting_gop",
    "custom_fields.behavior__ticket_splitting_dem",
    "custom_fields.political_activism_and_strife__political_donations",
    "custom_fields.ideology_partisanship__partisanship_overall",
    "custom_fields.ideology_partisanship__ideology_fiscal",
    "custom_fields.ideology_partisanship__ideology_social",
    "custom_fields.ideology_partisanship__partisanship_progressive_vs_moderate_dem",
    "custom_fields.ideology_partisanship__partisanship_establishment_vs_firebrand_gop",
    "custom_fields.candidates_and_officials__trump",
    "custom_fields.candidates_and_officials__jd_vance",
    "custom_fields.healthcare__abortion",
    "custom_fields.healthcare__medicare_for_all",
    "custom_fields.healthcare__obamacare_aca",
    "custom_fields.role_of_government__gun_control",
    "custom_fields.role_of_government__marijuana",
    "custom_fields.military_international_borders__mexican_border_wall",
    "custom_fields.military_international_borders__defense_spending",
    "custom_fields.environment__climate_change",
    "custom_fields.environment__green_new_deal",
    "custom_fields.economy__tax_cuts",
    "custom_fields.economy__economic_anxiety",
    "custom_fields.economy__inflation_fault",
    "custom_fields.economy__income_inequality",
    "custom_fields.education__school_choice",
    "custom_fields.education__school_spending",
    "custom_fields.political_activism_and_strife__critical_race_theory_books",
    "custom_fields.political_activism_and_strife__mass_deportations",
    "custom_fields.political_activism_and_strife__dei",
    "custom_fields.surus_voter_segmentation",
    "age_days",
    "reg_tenure_days",
]
