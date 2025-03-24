#!/usr/bin/env python3
import json
import os
from datetime import datetime

def generate_html(json_file_path):
    """
    Generate an HTML file to visualize the service extraction data
    """
    # Read the JSON file
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            print(f"Successfully loaded JSON data with {len(data)} items")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None
    
    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Service Extraction Visualization</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            body {
                display: flex;
                overflow-x: hidden;
            }
            .sidebar {
                width: 250px;
                min-width: 250px;
                background-color: #343a40;
                color: white;
                padding: 20px;
                height: 100vh;
                position: fixed;
                left: 0;
                top: 0;
                overflow-y: auto;
                z-index: 1000;
            }
            .main-content {
                margin-left: 250px;
                padding: 20px;
                width: calc(100% - 250px);
            }
            .card {
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .card-header {
                background-color: #f1f8ff;
                font-weight: bold;
                border-bottom: 1px solid #dee2e6;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .toggle-icon {
                transition: transform 0.3s ease;
            }
            .rotate-icon {
                transform: rotate(180deg);
            }
            .service-badge {
                background-color: #0d6efd;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                margin: 5px;
                display: inline-block;
            }
            .evidence-block {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #6c757d;
                font-family: monospace;
                white-space: pre-wrap;
                margin: 10px 0;
            }
            .reasoning-block {
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .file-path {
                color: #6c757d;
                font-size: 0.9rem;
                margin-bottom: 10px;
            }
            #search-input {
                margin-bottom: 20px;
            }
            .summary-section {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .service-count {
                font-size: 1.2rem;
                font-weight: bold;
                margin-right: 10px;
            }
            .sidebar-title {
                font-size: 1.2rem;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            .sidebar-service {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
                cursor: pointer;
                padding: 5px;
                border-radius: 5px;
                transition: background-color 0.2s;
            }
            .sidebar-service:hover {
                background-color: rgba(255,255,255,0.1);
            }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-title">Unique Services</div>
            <div id="unique-services-list">
                <!-- Services will be populated here -->
            </div>
        </div>
        <div class="main-content">
            <h1 class="my-4 text-center">Service Extraction Visualization</h1>
            
            <div class="row mb-4">
                <div class="col">
                    <input type="text" id="search-input" class="form-control" placeholder="Search for files, services, or keywords...">
                </div>
            </div>
            
            <div class="summary-section">
                <h2>Summary</h2>
                <div id="services-summary"></div>
            </div>
            
            <div id="file-cards">
            """
    
    # Track unique services for summary
    all_services = {}
    
    # Generate cards for each file
    for item in data:
        filename = item.get("filename", "Unknown file")
        message = item.get("message", {})
        reasoning = item.get("reasoning", "")
        
        detected_services = message.get("detected_data_sink_services", [])
        
        # Count services for summary
        print(f"Processing file: {filename}")
        print(f"Found {len(detected_services)} services in this file")
        for service_data in detected_services:
            service_name = service_data.get("service", "Unknown")
            print(f"Found service: {service_name}")
            if service_name in all_services:
                all_services[service_name] += 1
            else:
                all_services[service_name] = 1
        print(f"Current service counts: {all_services}")
        
        html_content += f"""
            <div class="card file-card">
                <div class="card-header" onclick="toggleCard(this)">
                    <div class="file-path">{filename}</div>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="card-body">
                    <h5>Detected Services:</h5>
                    <div class="services-container">
        """
        
        # Add service badges
        for service_data in detected_services:
            service_name = service_data.get("service", "Unknown")
            evidence = service_data.get("evidence", "")
            service_reasoning = service_data.get("reasoning", "")
            
            html_content += f"""
                        <div class="service-item mb-3">
                            <div class="service-badge">{service_name}</div>
                            <div class="evidence-block">{evidence}</div>
                            <div class="reasoning-block">
                                <strong>Reasoning:</strong> {service_reasoning}
                            </div>
                        </div>
            """
        
        html_content += """
                    </div>
                    <div class="mt-3">
                        <h5>Analysis:</h5>
                        <p>{}</p>
                    </div>
                </div>
            </div>
        """.format(reasoning)
    
    # Close the HTML content
    html_content += """
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Toggle card functionality
            function toggleCard(header) {
                const cardBody = header.nextElementSibling;
                const icon = header.querySelector('.toggle-icon');
                
                if (cardBody.style.display === 'none') {
                    cardBody.style.display = 'block';
                    icon.classList.remove('rotate-icon');
                } else {
                    cardBody.style.display = 'none';
                    icon.classList.add('rotate-icon');
                }
            }
            
            // Search functionality
            document.getElementById('search-input').addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const cards = document.querySelectorAll('.file-card');
                
                cards.forEach(card => {
                    const cardText = card.textContent.toLowerCase();
                    if (cardText.includes(searchTerm)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
            
            // Generate services summary
            const servicesData = {};
            console.log('Services data:', servicesData);
            
            // Summary section
            const summaryContainer = document.getElementById('services-summary');
            let summaryHTML = '<div class="row">';
            for (const [service, count] of Object.entries(servicesData)) {
                summaryHTML += `
                    <div class="col-md-4 mb-2">
                        <div class="d-flex align-items-center">
                            <span class="service-count">${count}</span>
                            <div class="service-badge">${service}</div>
                        </div>
                    </div>
                `;
            }
            summaryHTML += '</div>';
            summaryContainer.innerHTML = summaryHTML;
            
            // Sidebar unique services list
            const uniqueServicesList = document.getElementById('unique-services-list');
            if (!uniqueServicesList) {
                console.error('Could not find unique-services-list element');
            } else {
                console.log('Found unique-services-list element');
                let sidebarHTML = '';
                for (const [service, count] of Object.entries(servicesData)) {
                    sidebarHTML += `
                        <div class="sidebar-service" onclick="filterByService('${service.replace(/'/g, "\\'")}')"> <!-- Escape single quotes -->
                            <span class="service-count">${count}</span>
                            <div class="service-badge">${service}</div>
                        </div>
                    `;
                }
                uniqueServicesList.innerHTML = sidebarHTML;
                console.log('Updated sidebar HTML');
            }
            
            // Filter by service function
            function filterByService(serviceName) {
                const searchInput = document.getElementById('search-input');
                searchInput.value = serviceName;
                searchInput.dispatchEvent(new Event('input'));
            }
        </script>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """.replace("{}", json.dumps(all_services))
    
    # Write to HTML file
    if not all_services:
        print("Warning: No services were found in the data!")
    else:
        print(f"Total unique services found: {len(all_services)}")
        print(f"Service counts: {all_services}")
    
    output_file = os.path.join(os.path.dirname(json_file_path), "service_visualization.html")
    try:
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"HTML visualization created at: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        return None

if __name__ == "__main__":
    # Path to the JSON file
    json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "service_extraction.json")
    
    # Generate the HTML file
    html_file = generate_html(json_file_path)
    
    print(f"\nVisualization created at: {html_file}")
    print("You can open this file in your web browser to view the visualization.")
