"""
Module for the JavaScript functionality in the sidebar.
"""


def get_sidebar_javascript():
    """
    Get the JavaScript code for the sidebar functionality.

    Returns:
        String containing the JavaScript code
    """
    return """
        // Add Sortable.js from CDN
        function loadScript(url, callback) {
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = url;
            script.onload = callback;
            document.head.appendChild(script);
        }
        
        loadScript('https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js', function() {
            // Initialize Sortable on the column-order-list element
            var columnOrderList = document.getElementById('column-order-list');
            if (columnOrderList) {
                new Sortable(columnOrderList, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    chosenClass: 'sortable-chosen',
                    handle: '.sortable-handle',
                    onEnd: function(evt) {
                        // Get the current order and store it
                        storeColumnOrder();
                    }
                });
            }
        });
        
        // Handle custom messages from the server
        $(document).on('shiny:connected', function() {
            Shiny.addCustomMessageHandler('update_column_order_list', function(message) {
                if (message.action === 'update') {
                    updateColumnOrderList();
                }
            });
        });
        
        // Store the current column order
        function storeColumnOrder() {
            var columns = [];
            var items = document.querySelectorAll('#column-order-list .sortable-item');
            items.forEach(function(item) {
                columns.push(item.getAttribute('data-column'));
            });
            
            // Store the order in the hidden input field and trigger change event
            const orderInput = document.getElementById('column_order');
            orderInput.value = JSON.stringify(columns);
            
            // Dispatch change event to make sure Shiny detects the change
            const event = new Event('change', { bubbles: true });
            orderInput.dispatchEvent(event);
            
            // Add a visual indicator that the order has been saved
            const applyButton = document.getElementById('apply_order');
            if (applyButton) {
                applyButton.classList.add('bg-green-600');
                applyButton.textContent = 'Order Ready to Apply';
                
                // Reset the button after 2 seconds
                setTimeout(function() {
                    applyButton.classList.remove('bg-green-600');
                    applyButton.classList.add('bg-blue-600');
                    applyButton.textContent = 'Apply Order';
                }, 2000);
            }
        }
        
        // Update the column order list based on selected columns
        function updateColumnOrderList() {
            var columnOrderList = document.getElementById('column-order-list');
            
            // Clear existing items
            columnOrderList.innerHTML = '';
            
            // Get all selected columns
            var selectedColumns = [];
            
            // Process student info checkboxes
            const studentInfoCheckboxes = document.querySelectorAll('input[name="student_info_cols"]');
            studentInfoCheckboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    selectedColumns.push({
                        id: 'student_info_' + checkbox.value,
                        name: checkbox.value,
                        originalName: checkbox.value
                    });
                }
            });
            
            // Process assessment and grade checkboxes
            const assessmentAndGradeCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="col_"]');
            assessmentAndGradeCheckboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    // Find the label associated with this checkbox
                    const label = checkbox.parentNode.querySelector('label');
                    const columnName = label ? label.textContent.trim() : checkbox.id.substring(4);
                    const originalName = checkbox.getAttribute('data-original-name') || checkbox.id.substring(4).replace(/_/g, ' ');
                    
                    selectedColumns.push({
                        id: checkbox.id,
                        name: columnName,
                        originalName: originalName
                    });
                }
            });
            
            // Add items to the sortable list
            selectedColumns.forEach(function(column) {
                var item = document.createElement('div');
                item.className = 'sortable-item';
                item.setAttribute('data-column', column.originalName);
                item.innerHTML = '<i class="fas fa-grip-lines sortable-handle"></i> ' + column.name;
                columnOrderList.appendChild(item);
            });
            
            // Update the stored order
            storeColumnOrder();
        }
        
        // Toggle column selection section
        function toggleColumnSelection() {
            const content = document.getElementById('column-selection-content');
            const toggleBtn = document.getElementById('toggle-column-btn');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }

        // Toggle filters section
        function toggleFilters() {
            const content = document.getElementById('filters-content');
            const toggleBtn = document.getElementById('toggle-filters-btn');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }
        
        // Toggle column order section
        function toggleColumnOrder() {
            const content = document.getElementById('column-order-content');
            const toggleBtn = document.getElementById('toggle-order-btn');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
                updateColumnOrderList(); // Update the list when showing
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }
        
        // Toggle filter section
        function toggleFilterSection(sectionId) {
            const section = document.getElementById(sectionId);
            const header = section.previousElementSibling;
            const icon = header.querySelector('.toggle-filter-icon');
            
            if (section.style.display === 'none' || section.style.display === '') {
                section.style.display = 'block';
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-down');
            } else {
                section.style.display = 'none';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-right');
            }
        }
        
        // Initialize all filter sections as collapsed on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize filter sections
            const filterContents = document.querySelectorAll('.filter-content');
            filterContents.forEach(function(content) {
                content.style.display = 'none';
                const header = content.previousElementSibling;
                const icon = header.querySelector('.toggle-filter-icon');
                if (icon) {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-right');
                }
            });
            
            // Listen for changes in checkbox selections
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(function(checkbox) {
                checkbox.addEventListener('change', function() {
                    // Update the column order list when checkboxes change
                    updateColumnOrderList();
                });
            });
            
            // Initialize the column order list
            updateColumnOrderList();
        });
    """
