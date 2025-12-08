# industrial_datasets.py
"""
Industrial task datasets and templates for demonstrating
how the Time Tracker can be used in industrial environments.
"""

# Industrial task categories
CATEGORIES = [
    "MANUFACTURING", 
    "MAINTENANCE", 
    "QUALITY", 
    "LOGISTICS", 
    "ENGINEERING"
]

# Example tasks with industrial categories and standard times (in seconds)
INDUSTRIAL_TASKS = {
    "CNC_MACHINING": {
        "category": "MANUFACTURING",
        "description": "Computer Numerical Control machining operations",
        "tasks": {
            "setup": {
                "name": "Machine Setup",
                "description": "Setup CNC machine, load program, and prepare tools",
                "standard_time": 900,  # 15 minutes
                "assigned_to": "Machine Operator"
            },
            "calibration": {
                "name": "Tool Calibration",
                "description": "Calibrate cutting tools and verify measurements",
                "standard_time": 480,  # 8 minutes
                "assigned_to": "CNC Technician"
            },
            "batch_run": {
                "name": "Batch Production Run",
                "description": "Execute production batch with continuous monitoring",
                "standard_time": 2700,  # 45 minutes
                "assigned_to": "Machine Operator"
            },
            "inspection": {
                "name": "Quality Inspection",
                "description": "Measure parts and verify tolerances",
                "standard_time": 720,  # 12 minutes
                "assigned_to": "Quality Inspector"
            },
            "cleanup": {
                "name": "Machine Cleanup",
                "description": "Clean machine, remove chips, and organize workspace",
                "standard_time": 420,  # 7 minutes
                "assigned_to": "Machine Operator"
            }
        }
    },
    "WELDING": {
        "category": "MANUFACTURING",
        "description": "Metal welding and fabrication operations",
        "tasks": {
            "material_prep": {
                "name": "Material Preparation",
                "description": "Cut, fit, and prepare materials for welding",
                "standard_time": 600,  # 10 minutes
                "assigned_to": "Welder"
            },
            "welding": {
                "name": "Welding Operation",
                "description": "Perform welding according to specifications",
                "standard_time": 1500,  # 25 minutes
                "assigned_to": "Certified Welder"
            },
            "grinding": {
                "name": "Weld Grinding",
                "description": "Grind and smooth welded joints",
                "standard_time": 900,  # 15 minutes
                "assigned_to": "Welder"
            },
            "inspection": {
                "name": "Weld Inspection",
                "description": "Visual and non-destructive testing of welds",
                "standard_time": 480,  # 8 minutes
                "assigned_to": "Weld Inspector"
            }
        }
    },
    "MAINTENANCE": {
        "category": "MAINTENANCE",
        "description": "Equipment maintenance and repair operations",
        "tasks": {
            "lockout": {
                "name": "Lockout/Tagout",
                "description": "Implement safety lockout procedures",
                "standard_time": 300,  # 5 minutes
                "assigned_to": "Maintenance Technician"
            },
            "fluid_change": {
                "name": "Fluid Change",
                "description": "Drain and replace hydraulic/lubricating fluids",
                "standard_time": 1500,  # 25 minutes
                "assigned_to": "Maintenance Technician"
            },
            "lubrication": {
                "name": "Equipment Lubrication",
                "description": "Lubricate moving parts and bearings",
                "standard_time": 900,  # 15 minutes
                "assigned_to": "Maintenance Technician"
            },
            "alignment": {
                "name": "Equipment Alignment",
                "description": "Check and adjust equipment alignment",
                "standard_time": 1200,  # 20 minutes
                "assigned_to": "Maintenance Engineer"
            },
            "test": {
                "name": "Functionality Test",
                "description": "Test equipment operation and performance",
                "standard_time": 600,  # 10 minutes
                "assigned_to": "Maintenance Technician"
            }
        }
    },
    "ASSEMBLY_LINE": {
        "category": "MANUFACTURING",
        "description": "Assembly line and production operations",
        "tasks": {
            "station_setup": {
                "name": "Assembly Station Setup",
                "description": "Prepare workstation with tools and materials",
                "standard_time": 600,  # 10 minutes
                "assigned_to": "Assembly Operator"
            },
            "component_assembly": {
                "name": "Component Assembly",
                "description": "Assemble components according to work instructions",
                "standard_time": 1800,  # 30 minutes
                "assigned_to": "Assembly Operator"
            },
            "quality_check": {
                "name": "In-line Quality Check",
                "description": "Perform quality checks during assembly",
                "standard_time": 480,  # 8 minutes
                "assigned_to": "Assembly Lead"
            },
            "packaging": {
                "name": "Product Packaging",
                "description": "Package finished products for shipping",
                "standard_time": 720,  # 12 minutes
                "assigned_to": "Packaging Operator"
            }
        }
    },
    "QUALITY_CONTROL": {
        "category": "QUALITY",
        "description": "Quality control and inspection operations",
        "tasks": {
            "incoming_inspection": {
                "name": "Incoming Material Inspection",
                "description": "Inspect received materials for quality compliance",
                "standard_time": 900,  # 15 minutes
                "assigned_to": "QC Inspector"
            },
            "dimensional_inspection": {
                "name": "Dimensional Inspection",
                "description": "Measure and verify part dimensions",
                "standard_time": 1200,  # 20 minutes
                "assigned_to": "QC Inspector"
            },
            "functional_test": {
                "name": "Functional Testing",
                "description": "Test product functionality and performance",
                "standard_time": 1800,  # 30 minutes
                "assigned_to": "Test Technician"
            },
            "documentation": {
                "name": "Quality Documentation",
                "description": "Complete inspection reports and certificates",
                "standard_time": 600,  # 10 minutes
                "assigned_to": "QC Inspector"
            }
        }
    },
    "LOGISTICS": {
        "category": "LOGISTICS",
        "description": "Material handling and logistics operations",
        "tasks": {
            "receiving": {
                "name": "Material Receiving",
                "description": "Receive, verify, and log incoming materials",
                "standard_time": 1200,  # 20 minutes
                "assigned_to": "Warehouse Clerk"
            },
            "inventory": {
                "name": "Inventory Count",
                "description": "Conduct physical inventory count and verification",
                "standard_time": 2700,  # 45 minutes
                "assigned_to": "Inventory Specialist"
            },
            "picking": {
                "name": "Order Picking",
                "description": "Pick items from warehouse for production",
                "standard_time": 900,  # 15 minutes
                "assigned_to": "Warehouse Operator"
            },
            "shipping": {
                "name": "Shipping Preparation",
                "description": "Prepare and document shipments",
                "standard_time": 1500,  # 25 minutes
                "assigned_to": "Shipping Clerk"
            }
        }
    },
    "ENGINEERING": {
        "category": "ENGINEERING",
        "description": "Engineering and process improvement tasks",
        "tasks": {
            "design_review": {
                "name": "Design Review",
                "description": "Review and approve technical designs",
                "standard_time": 3600,  # 60 minutes
                "assigned_to": "Design Engineer"
            },
            "process_study": {
                "name": "Time and Motion Study",
                "description": "Conduct process analysis and optimization",
                "standard_time": 5400,  # 90 minutes
                "assigned_to": "Industrial Engineer"
            },
            "documentation": {
                "name": "Technical Documentation",
                "description": "Create or update technical documentation",
                "standard_time": 2700,  # 45 minutes
                "assigned_to": "Technical Writer"
            },
            "root_cause": {
                "name": "Root Cause Analysis",
                "description": "Investigate and resolve production issues",
                "standard_time": 4200,  # 70 minutes
                "assigned_to": "Process Engineer"
            }
        }
    }
}


def get_all_categories():
    """Return list of all industrial categories."""
    return CATEGORIES


def get_task_groups():
    """Return list of all task group names."""
    return list(INDUSTRIAL_TASKS.keys())


def get_tasks_by_group(group_name):
    """
    Get all tasks for a specific industrial group.
    
    Args:
        group_name: Name of the industrial task group (e.g., "CNC_MACHINING")
        
    Returns:
        Dictionary of tasks with their details, or None if group not found
    """
    if group_name in INDUSTRIAL_TASKS:
        return INDUSTRIAL_TASKS[group_name]["tasks"]
    return None


def get_category_for_group(group_name):
    """Get the category for a specific task group."""
    if group_name in INDUSTRIAL_TASKS:
        return INDUSTRIAL_TASKS[group_name]["category"]
    return None


def get_all_tasks_flat():
    """
    Get all tasks as a flat list with full details.
    
    Returns:
        List of dictionaries containing task details with group and category info
    """
    all_tasks = []
    for group_name, group_data in INDUSTRIAL_TASKS.items():
        category = group_data["category"]
        for task_key, task_data in group_data["tasks"].items():
            task_info = task_data.copy()
            task_info["group"] = group_name
            task_info["category"] = category
            task_info["task_key"] = task_key
            all_tasks.append(task_info)
    return all_tasks
