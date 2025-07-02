"""
Module for the CSS styles used in the sidebar.
"""


def get_sidebar_styles():
    """
    Get the CSS styles for the sidebar.

    Returns:
        String containing the CSS styles
    """
    return """
        /* Make the sidebar take up more space */
        .sidebar {
            min-width: 300px;
            width: 100%;
            max-width: 360px;
        }
        
        /* Make the Column Selection title more prominent */
        .sidebar h3 {
            font-size: 1.1rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            padding-left: 8px;
            display: inline-block;
        }
        
        /* Toggle button styling */
        .toggle-button {
            float: right;
            margin-top: 0.5rem;
            margin-right: 0.5rem;
            cursor: pointer;
            color: #4b5563;
            transition: color 0.2s;
        }
        
        .toggle-button:hover {
            color: #1e40af;
        }
        
        /* Header container with flex layout */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 8px;
            margin-bottom: 0.5rem;
        }
        
        /* Take up full height */
        .navset-card-tab {
            height: calc(100vh - 100px);
            display: flex;
            flex-direction: column;
        }
        
        /* Make tabs fill width */
        .nav-tabs {
            width: 100%;
            display: flex;
        }
        
        .nav-tabs .nav-item {
            flex-grow: 1;
            text-align: center;
        }
        
        /* Make tab panels fill available height */
        .tab-content {
            flex: 1;
            min-height: 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .tab-pane {
            flex: 1;
            overflow-y: auto;
            position: relative;
        }
        
        .tab-pane.active {
            display: flex;
            flex-direction: column;
        }
        
        /* Tree structure styling */
        .assessment-tree, .filter-section {
            padding: 8px;
            height: 100%;
            overflow-y: auto;
        }
        
        .tree-node {
            margin-bottom: 2px;
        }
        
        .tree-branch {
            display: flex;
            align-items: center;
        }
        
        .tree-branch-header {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 6px 8px;
            flex-grow: 1;
            width: 100%;
            border-radius: 0.25rem;
            transition: background-color 0.2s;
        }
        
        .tree-branch-header:hover {
            background-color: #f0f0f0;
        }
        
        .tree-icon {
            margin-right: 8px;
            color: #4b5563;
            width: 14px;
        }
        
        .tree-branch-label {
            cursor: pointer;
            margin-bottom: 0;
            font-size: 0.95rem;
            width: calc(100% - 22px);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
        }
        
        .tree-children {
            margin-left: 12px;
            border-left: 1px dashed #cbd5e1;
            padding-left: 8px;
            overflow: hidden;
            max-height: 2000px;
            transition: max-height 0.3s ease-out, opacity 0.3s;
        }
        
        .tree-children.collapsed {
            max-height: 0;
            opacity: 0;
            transition: max-height 0.2s ease-out, opacity 0.2s;
        }
        
        .tree-leaf {
            display: flex;
            align-items: center;
            margin: 3px 0;
            padding: 4px 6px;
            border-radius: 0.25rem;
        }
        
        .tree-leaf:hover {
            background-color: #e2e8f0;
        }
        
        /* Make the checkboxes more appealing */
        .form-check-input {
            margin-top: 0;
            margin-left: 0;
            border-radius: 0.25rem;
            border: 1px solid #cbd5e1;
        }
        
        /* Font sizes for different levels */
        .tree-node > .tree-branch .tree-branch-label {
            font-weight: 600;
            font-size: 1rem;
            color: #1e40af;
        }
        
        /* Filters section styling */
        .filter-section h2 {
            color: #1e40af;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
        }
        
        .filter-section h3 {
            color: #2563eb;
            font-size: 1.05rem;
        }
        
        .filter-section h4 {
            color: #4b5563;
            font-size: 0.95rem;
            display: inline-block;
        }
        
        /* Filter header styling */
        .filter-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .filter-header:hover {
            background-color: #f3f4f6;
        }
        
        .toggle-filter-icon {
            color: #6b7280;
            transition: transform 0.2s;
        }
        
        /* Selectize styling */
        .selectize-control {
            width: 100%;
        }
        
        .selectize-dropdown-content {
            max-height: 200px;
        }
        
        .selectize-control.multi .selectize-input {
            padding: 6px 8px;
        }
        
        .selectize-control.multi .selectize-input > div {
            margin: 2px 3px;
            padding: 1px 5px;
            background: #e2e8f0;
            color: #4b5563;
            border-radius: 3px;
        }
        
        /* Column ordering styles */
        .column-order-container {
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            min-height: 50px;
            max-height: 300px;
            overflow-y: auto;
            background-color: #f8fafc;
        }
        
        .sortable-item {
            padding: 0.5rem;
            margin: 4px;
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            cursor: grab;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            transition: all 0.2s;
        }
        
        .sortable-item:hover {
            background-color: #f1f5f9;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .sortable-item.sortable-ghost {
            opacity: 0.5;
            background-color: #e2e8f0;
        }
        
        .sortable-item.sortable-chosen {
            background-color: #e2e8f0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .sortable-handle {
            color: #94a3b8;
            cursor: grab;
            margin-right: 8px;
        }
        
        /* Divider styling */
        .sidebar-divider {
            margin: 1rem 0;
            border-top: 1px solid #e2e8f0;
        }
    """
