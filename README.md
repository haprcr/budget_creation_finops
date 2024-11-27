# Budget Creation for FinOps  
**Script for Scalable Deployment of Budgets and Notification Channels**

This repository contains scripts to programmatically create budgets and notification channels in Google Cloud Platform (GCP) using the **Cloud Billing Budget API**. These scripts streamline budget deployment at scale, supporting FinOps strategies for cost management.

---

## Overview  
The **Budget API** enables programmatic creation and management of budgets for GCP projects. This repository provides a Python-based implementation for creating budgets and notification channels via the Cloud Billing Budget API Client Library. 

---

## Features  
- **Budget creation**: Define budgets for specific projects and billing accounts.  
- **Notification channel creation**: Configure alerts to notify stakeholders when spending thresholds are met.  
- **Customizable parameters**: Supports custom threshold rules, periods, and budget amounts.  

---

## Prerequisites  

### 1. Budget Input Sheet  
Prepare a file named `budget_list.xlsx` with the required budget details.  

#### Fields and Definitions:
| **Field**              | **Description**                                                                                      |
|------------------------|-----------------------------------------------------------------------------------------------------|
| **billing_account_id** | ID of the billing account associated with the project.                                              |
| **display_Name**       | A short, human-readable name for the budget.                                                        |
| **project_ID**         | Project ID to which the budget applies.                                                             |
| **calendar_Period**    | Time period for tracking spending. Options: `YEAR`, `QUARTER`, `MONTH`, or a custom period.         |
| **budget_Amount**      | Budgeted amount per usage period (can be a specific value or "Last calendar period spend").          |
| **email_Id_List**      | List of email IDs to receive budget alert notifications.                                            |
| **threshold_Rules**    | Conditions for triggering notifications based on spending percentages and spending basis.           |

#### Threshold Rules Specification Example:  
| **thresholdPercent** | **spendBasis**  |
|-----------------------|-----------------|
| `[0.9, 0.6, 0.5, 0.8]` | `CURRENT_SPEND` |

---

### 2. Service Account  
Create a **service account** with the required permissions at the organization level.

#### Predefined Roles:  
- `Project Owner` or `Project Editor`

#### Custom Role Permissions:  
- `resourcemanager.projects.get`  
- `billing.resourceCosts.get`  
- `billing.resourcebudgets.read`  
- `billing.resourcebudgets.write`  

Update the **Service Account ID** in the following files:
- `create_budget.py`  
- `delete_budget.py`  
- `delete_channel.py`  

#### Assign Required Role:  
Grant the **Service Account Token Creator** role to the user or identity executing the script.  

---

## Folder Structure

```
├── budget_list.xlsx        # Input file for budget details
├── create_budget.py        # Script for creating budgets
├── delete_budget.py        # Script for deleting budgets
├── delete_channel.py       # Script for removing notification channels
├── requirements.txt        # List of dependencies
├── script.sh               # Automated setup script
└── README.md               # Documentation
```
---
## Installation  

1. **Create and Activate a Virtual Environment**:  
   ```bash
   sudo apt install python3.11-venv  # If venv is not installed  
   python3 -m venv <your-venv-name>  
   source <your-venv-name>/bin/activate  


2. **Install Dependencies (run only during the initial setup)**:  
   ```bash
   chmod +x script.sh  
   ./script.sh


3. **Execution**:
Run the Python script to create budgets:
   ```bash
    python3 create_budget.py


