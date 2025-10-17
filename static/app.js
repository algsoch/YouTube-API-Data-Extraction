// JavaScript for YouTube Data Extraction App

// Global state
let statusUpdateInterval = null;
let progressChart = null;

// Initialize app on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeNavigation();
    startStatusPolling();
});

// Initialize application
function initializeApp() {
    console.log('Initializing YouTube Data Extraction App...');
    refreshStatus();
    loadQueries();
    initializeProgressChart();
}

// Navigation handling
function initializeNavigation() {
    document.querySelectorAll('[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            navigateToPage(page);
        });
    });
}

function navigateToPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.add('d-none');
    });
    
    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.remove('d-none');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    // Load page-specific data
    if (pageName === 'files') {
        loadFiles();
    } else if (pageName === 'analysis') {
        loadAnalysis('overview');
    } else if (pageName === 'data-tables') {
        loadDataTable('videos');
    }
}

// Status polling
function startStatusPolling() {
    statusUpdateInterval = setInterval(refreshStatus, 5000); // Update every 5 seconds
}

async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        updateStatusDisplay(status);
        
        // Also update progress
        const progressResponse = await fetch('/api/progress');
        const progress = await progressResponse.json();
        updateProgressDisplay(progress);
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

function updateStatusDisplay(status) {
    // Update stat cards
    document.getElementById('stat-videos').textContent = status.videos_collected.toLocaleString();
    document.getElementById('stat-channels').textContent = status.channels_collected.toLocaleString();
    document.getElementById('stat-queries').textContent = `${status.completed_queries.length} / ${status.total_queries || 17}`;
    document.getElementById('stat-quota').textContent = status.quota_used.toLocaleString();
    
    // Update progress bar
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${status.progress}%`;
    progressBar.textContent = `${status.progress}%`;
    
    // Update status alerts
    if (status.is_running) {
        document.getElementById('status-running').classList.remove('d-none');
        document.getElementById('status-idle').classList.add('d-none');
        document.getElementById('current-query').textContent = status.current_query || 'Starting...';
        document.getElementById('start-btn').classList.add('d-none');
        document.getElementById('stop-btn').classList.remove('d-none');
    } else {
        document.getElementById('status-running').classList.add('d-none');
        document.getElementById('status-idle').classList.remove('d-none');
        document.getElementById('start-btn').classList.remove('d-none');
        document.getElementById('stop-btn').classList.add('d-none');
    }
    
    // Update errors with better formatting
    if (status.errors && status.errors.length > 0) {
        document.getElementById('error-container').classList.remove('d-none');
        const errorList = document.getElementById('error-list');
        errorList.innerHTML = status.errors.map(err => {
            let icon = 'fa-exclamation-triangle';
            let colorClass = 'text-danger';
            
            // Use different icons for different message types
            if (err.includes('✅')) {
                icon = 'fa-check-circle';
                colorClass = 'text-success';
            } else if (err.includes('🕒')) {
                icon = 'fa-clock';
                colorClass = 'text-info';
            } else if (err.includes('💡')) {
                icon = 'fa-lightbulb';
                colorClass = 'text-warning';
            } else if (err.includes('⚠️')) {
                icon = 'fa-exclamation-circle';
                colorClass = 'text-warning';
            }
            
            return `<li class="${colorClass}"><i class="fas ${icon}"></i> ${err}</li>`;
        }).join('');
    } else {
        document.getElementById('error-container').classList.add('d-none');
    }
    
    // Display quota reset information if quota exceeded
    if (status.quota_exceeded && status.quota_reset_info) {
        const resetInfo = status.quota_reset_info;
        const resetMessage = `⏰ Quota resets in: ${resetInfo.formatted} (at ${new Date(resetInfo.reset_time).toLocaleTimeString()})`;
        
        // Show quota exceeded alert banner on dashboard
        const quotaAlert = document.getElementById('quota-exceeded-alert');
        if (quotaAlert) {
            quotaAlert.classList.remove('d-none');
            document.getElementById('quota-reset-timer').textContent = resetInfo.formatted;
            document.getElementById('quota-reset-time').textContent = new Date(resetInfo.reset_time).toLocaleString();
        }
        
        // Show quota exceeded alert banner on extraction page
        const quotaAlertExtraction = document.getElementById('quota-exceeded-alert-extraction');
        if (quotaAlertExtraction) {
            quotaAlertExtraction.classList.remove('d-none');
            document.getElementById('quota-reset-timer-extraction').textContent = resetInfo.formatted;
            document.getElementById('quota-reset-time-extraction').textContent = new Date(resetInfo.reset_time).toLocaleString();
        }
        
        // Add quota reset info to errors if not already there
        if (!status.errors.some(e => e.includes('Quota resets in'))) {
            const errorList = document.getElementById('error-list');
            const resetItem = document.createElement('li');
            resetItem.className = 'text-info fw-bold';
            resetItem.innerHTML = `<i class="fas fa-clock"></i> ${resetMessage}`;
            errorList.appendChild(resetItem);
        }
    } else {
        // Hide quota exceeded alerts if not exceeded
        const quotaAlert = document.getElementById('quota-exceeded-alert');
        if (quotaAlert) {
            quotaAlert.classList.add('d-none');
        }
        const quotaAlertExtraction = document.getElementById('quota-exceeded-alert-extraction');
        if (quotaAlertExtraction) {
            quotaAlertExtraction.classList.add('d-none');
        }
    }
    
    // Update timestamp
    if (status.last_updated) {
        const date = new Date(status.last_updated);
        document.getElementById('last-updated').textContent = date.toLocaleString();
    }
}

function updateProgressDisplay(progress) {
    // Update chart if needed
    if (progressChart && progress.completed_queries) {
        updateProgressChart(progress.completed_queries);
    }
}

// Extraction control
async function startExtraction() {
    const videosPerQuery = parseInt(document.getElementById('videos-per-query').value);
    const quotaLimit = parseInt(document.getElementById('quota-limit').value);
    
    try {
        const response = await fetch('/api/extract/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                videos_per_query: videosPerQuery,
                daily_quota: quotaLimit
            })
        });
        
        if (response.ok) {
            showToast('Extraction started successfully!', 'success');
            refreshStatus();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to start extraction', 'danger');
        }
    } catch (error) {
        console.error('Error starting extraction:', error);
        showToast('Failed to start extraction', 'danger');
    }
}

async function stopExtraction() {
    try {
        const response = await fetch('/api/extract/stop', {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Stop requested. Extraction will stop after current operation.', 'warning');
            refreshStatus();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to stop extraction', 'danger');
        }
    } catch (error) {
        console.error('Error stopping extraction:', error);
        showToast('Failed to stop extraction', 'danger');
    }
}

// Load search queries
async function loadQueries() {
    try {
        const [queriesResponse, progressResponse] = await Promise.all([
            fetch('/api/queries'),
            fetch('/api/progress')
        ]);
        
        const queries = await queriesResponse.json();
        const progress = await progressResponse.json();
        
        const queriesList = document.getElementById('queries-list');
        queriesList.innerHTML = queries.queries.map(query => {
            const isCompleted = progress.completed_queries.includes(query);
            const itemClass = isCompleted ? 'list-group-item completed' : 'list-group-item';
            const icon = isCompleted ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-circle text-muted"></i>';
            
            return `<li class="${itemClass}">${icon} ${query}</li>`;
        }).join('');
    } catch (error) {
        console.error('Error loading queries:', error);
    }
}

// Progress Chart
function initializeProgressChart() {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    progressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Videos Collected',
                data: [],
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 500
                    }
                }
            }
        }
    });
}

function updateProgressChart(completedQueries) {
    if (!progressChart) return;
    
    progressChart.data.labels = completedQueries.slice(0, 10);
    progressChart.data.datasets[0].data = completedQueries.slice(0, 10).map(() => 2000);
    progressChart.update();
}

// Analysis functions
async function loadAnalysis(type) {
    const content = document.getElementById('analysis-content');
    content.innerHTML = '<div class="text-center py-5"><div class="spinner-border" role="status"></div><p class="mt-2">Loading analysis...</p></div>';
    
    try {
        let data;
        switch (type) {
            case 'overview':
                data = await fetchAnalysisOverview();
                renderOverviewAnalysis(data);
                break;
            case 'channels':
                data = await fetchTopChannels();
                renderChannelsAnalysis(data);
                break;
            case 'temporal':
                data = await fetchTemporalAnalysis();
                renderTemporalAnalysis(data);
                break;
            case 'engagement':
                data = await fetchEngagementAnalysis();
                renderEngagementAnalysis(data);
                break;
        }
    } catch (error) {
        console.error('Error loading analysis:', error);
        content.innerHTML = '<div class="alert alert-danger">Failed to load analysis. Make sure data has been collected.</div>';
    }
}

async function fetchAnalysisOverview() {
    const response = await fetch('/api/analysis/overview');
    return await response.json();
}

async function fetchTopChannels() {
    const response = await fetch('/api/analysis/channels/top?limit=20');
    return await response.json();
}

async function fetchTemporalAnalysis() {
    const response = await fetch('/api/analysis/temporal');
    return await response.json();
}

async function fetchEngagementAnalysis() {
    const response = await fetch('/api/analysis/engagement');
    return await response.json();
}

function renderOverviewAnalysis(data) {
    const content = document.getElementById('analysis-content');
    content.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <div class="analysis-metric">
                    <h6>Total Videos</h6>
                    <div class="value">${data.total_videos?.toLocaleString() || 0}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="analysis-metric">
                    <h6>Total Channels</h6>
                    <div class="value">${data.total_channels?.toLocaleString() || 0}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="analysis-metric">
                    <h6>Total Views</h6>
                    <div class="value">${formatNumber(data.total_views) || 0}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="analysis-metric">
                    <h6>Total Subscribers</h6>
                    <div class="value">${formatNumber(data.total_subscribers) || 0}</div>
                </div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5>Date Range</h5>
                        <p>Earliest: ${data.date_range?.earliest || 'N/A'}</p>
                        <p>Latest: ${data.date_range?.latest || 'N/A'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderChannelsAnalysis(data) {
    const content = document.getElementById('analysis-content');
    if (!data.top_channels || data.top_channels.length === 0) {
        content.innerHTML = '<div class="alert alert-info">No channel data available yet.</div>';
        return;
    }
    
    content.innerHTML = `
        <div class="row">
            ${data.top_channels.map((channel, index) => `
                <div class="col-md-6 col-lg-4">
                    <div class="channel-card">
                        <h6 class="mb-2">${index + 1}. ${channel.title}</h6>
                        <div class="channel-stats">
                            <div class="channel-stat">
                                <span class="channel-stat-label">Subscribers</span>
                                <span class="channel-stat-value">${formatNumber(channel.subscriberCount)}</span>
                            </div>
                            <div class="channel-stat">
                                <span class="channel-stat-label">Views</span>
                                <span class="channel-stat-value">${formatNumber(channel.viewCount)}</span>
                            </div>
                            <div class="channel-stat">
                                <span class="channel-stat-label">Videos</span>
                                <span class="channel-stat-value">${channel.videoCount}</span>
                            </div>
                        </div>
                        ${channel.country ? `<small class="text-muted"><i class="fas fa-globe"></i> ${channel.country}</small>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderTemporalAnalysis(data) {
    const content = document.getElementById('analysis-content');
    content.innerHTML = '<div class="card"><div class="card-body"><canvas id="temporalChart"></canvas></div></div>';
    
    const ctx = document.getElementById('temporalChart');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(data.by_month || {}),
            datasets: [{
                label: 'Videos Published',
                data: Object.values(data.by_month || {}),
                borderColor: 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Videos Published Over Time'
                }
            }
        }
    });
}

function renderEngagementAnalysis(data) {
    const content = document.getElementById('analysis-content');
    content.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <div class="analysis-metric">
                    <h6>Avg Views/Video</h6>
                    <div class="value">${formatNumber(data.avg_views_per_video)}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="analysis-metric">
                    <h6>Avg Views/Subscriber</h6>
                    <div class="value">${data.avg_views_per_subscriber?.toFixed(2) || 0}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="analysis-metric">
                    <h6>Total Reach</h6>
                    <div class="value">${formatNumber(data.total_reach?.views)}</div>
                </div>
            </div>
        </div>
    `;
}

// Files management
async function loadFiles() {
    try {
        const response = await fetch('/api/files');
        const data = await response.json();
        
        const tbody = document.querySelector('#files-table tbody');
        if (!data.files || data.files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No files available</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.files.map(file => `
            <tr>
                <td><i class="fas fa-file-csv"></i> ${file.name}</td>
                <td><span class="badge bg-secondary file-size-badge">${formatFileSize(file.size)}</span></td>
                <td>${new Date(file.modified).toLocaleString()}</td>
                <td>
                    <a href="/api/files/download/${file.name}" class="btn btn-sm btn-primary" download>
                        <i class="fas fa-download"></i> Download
                    </a>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

// Custom Query Functions
async function fetchCustomQuery() {
    const query = document.getElementById('custom-search-query').value.trim();
    const maxVideos = parseInt(document.getElementById('custom-max-videos').value);
    
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    const btn = document.getElementById('fetch-custom-btn');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/query/custom', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                max_videos: maxVideos
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayCustomQueryResults(data);
            showToast('Data fetched successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to fetch data', 'danger');
        }
    } catch (error) {
        console.error('Error fetching custom query:', error);
        showToast('Failed to fetch data', 'danger');
    } finally {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}

function displayCustomQueryResults(data) {
    const resultsDiv = document.getElementById('custom-query-results');
    
    resultsDiv.innerHTML = `
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5><i class="fas fa-check-circle"></i> Results for: "${data.query}"</h5>
            </div>
            <div class="card-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="text-center">
                            <h3 class="text-primary">${data.video_count}</h3>
                            <p class="text-muted">Videos Found</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h3 class="text-success">${data.channel_count}</h3>
                            <p class="text-muted">Unique Channels</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h3 class="text-warning">${data.quota_used}</h3>
                            <p class="text-muted">Quota Used</p>
                        </div>
                    </div>
                </div>
                
                <h6>Sample Videos (First 10)</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Channel</th>
                                <th>Published</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.videos.slice(0, 10).map(video => `
                                <tr>
                                    <td><a href="https://youtube.com/watch?v=${video.videoId}" target="_blank">${video.title}</a></td>
                                    <td>${video.channelTitle}</td>
                                    <td>${new Date(video.publishedAt).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Data Table Functions
let currentTableType = 'videos';
let currentPage = 1;
let pageSize = 50;
let totalRecords = 0;
let currentSearch = '';

async function loadDataTable(type) {
    currentTableType = type;
    currentPage = 1;
    currentSearch = '';
    document.getElementById('table-search').value = '';
    
    // Update button states
    document.getElementById('btn-videos-table').className = type === 'videos' ? 'btn btn-primary' : 'btn btn-outline-primary';
    document.getElementById('btn-channels-table').className = type === 'channels' ? 'btn btn-primary' : 'btn btn-outline-primary';
    
    await fetchTableData();
}

async function fetchTableData() {
    try {
        const skip = (currentPage - 1) * pageSize;
        const endpoint = currentTableType === 'videos' ? '/api/data/videos' : '/api/data/channels';
        const response = await fetch(`${endpoint}?skip=${skip}&limit=${pageSize}&search=${encodeURIComponent(currentSearch)}`);
        
        if (!response.ok) {
            showToast('No data available yet. Please run extraction first.', 'info');
            return;
        }
        
        const data = await response.json();
        totalRecords = data.total;
        
        renderTable(data.data, currentTableType);
        updatePagination();
    } catch (error) {
        console.error('Error fetching table data:', error);
        showToast('Failed to load data', 'danger');
    }
}

function renderTable(data, type) {
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    
    if (type === 'videos') {
        tableHead.innerHTML = `
            <tr>
                <th style="width: 40%">Title</th>
                <th>Channel</th>
                <th>Published</th>
                <th>Video ID</th>
            </tr>
        `;
        
        tableBody.innerHTML = data.map(video => `
            <tr>
                <td>
                    <a href="https://youtube.com/watch?v=${video.videoId}" target="_blank" class="text-decoration-none">
                        ${video.title || 'N/A'}
                    </a>
                </td>
                <td>${video.channelTitle || 'N/A'}</td>
                <td>${video.publishedAt ? new Date(video.publishedAt).toLocaleDateString() : 'N/A'}</td>
                <td><code>${video.videoId}</code></td>
            </tr>
        `).join('');
    } else {
        tableHead.innerHTML = `
            <tr>
                <th style="width: 30%">Channel Name</th>
                <th>Subscribers</th>
                <th>Views</th>
                <th>Videos</th>
                <th>Country</th>
            </tr>
        `;
        
        tableBody.innerHTML = data.map(channel => `
            <tr>
                <td>
                    <a href="https://youtube.com/channel/${channel.channelId}" target="_blank" class="text-decoration-none">
                        ${channel.title || 'N/A'}
                    </a>
                </td>
                <td>${formatNumber(channel.subscriberCount)}</td>
                <td>${formatNumber(channel.viewCount)}</td>
                <td>${formatNumber(channel.videoCount)}</td>
                <td>${channel.country || 'N/A'}</td>
            </tr>
        `).join('');
    }
    
    document.getElementById('table-total-count').textContent = `Total: ${totalRecords}`;
}

function updatePagination() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    document.getElementById('current-page').textContent = currentPage;
    document.getElementById('total-pages').textContent = totalPages;
    
    document.getElementById('btn-prev').disabled = currentPage === 1;
    document.getElementById('btn-next').disabled = currentPage >= totalPages;
}

async function nextPage() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (currentPage < totalPages) {
        currentPage++;
        await fetchTableData();
    }
}

async function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        await fetchTableData();
    }
}

async function searchTable() {
    currentSearch = document.getElementById('table-search').value.trim();
    currentPage = 1;
    await fetchTableData();
}

// Utility functions
function formatNumber(num) {
    if (!num) return '0';
    num = parseFloat(num);
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showToast(message, type = 'info') {
    // Simple toast notification (you can enhance this with Bootstrap toast)
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    alert.style.zIndex = '9999';
    alert.innerHTML = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// ============================================================================
// ADVANCED ANALYTICS FUNCTIONS
// ============================================================================

async function loadAdvancedAnalytics() {
    try {
        const response = await fetch('/api/analytics/dashboard');
        const data = await response.json();
        
        // Populate overview stats
        populateOverviewStats(data.video_statistics, data.overview);
        
        // Load rankings
        if (data.rankings) {
            populateRankingsData(data.rankings);
        }
        
        // Create charts
        createAnalyticsCharts(data.video_statistics);
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Error loading analytics data', 'danger');
    }
}

function populateOverviewStats(videoStats, overview) {
    const statsContainer = document.getElementById('overview-stats');
    if (!statsContainer || !videoStats) return;
    
    const stats = [
        { title: 'Total Videos', value: videoStats.total_videos || 0, icon: 'video', color: 'primary' },
        { title: 'Unique Channels', value: videoStats.unique_channels || 0, icon: 'users', color: 'success' },
        { title: 'Search Queries', value: videoStats.unique_queries || 0, icon: 'search', color: 'info' },
        { title: 'Date Span (Days)', value: videoStats.date_range?.span_days || 0, icon: 'calendar', color: 'warning' }
    ];
    
    statsContainer.innerHTML = stats.map(stat => `
        <div class="col-md-3">
            <div class="card text-white bg-${stat.color}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title text-white-50">${stat.title}</h6>
                            <h3 class="mb-0">${formatNumber(stat.value)}</h3>
                        </div>
                        <i class="fas fa-${stat.icon} fa-3x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function populateRankingsData(rankings) {
    // Most Subscribed
    if (rankings.most_subscribed) {
        populateRankingTable('most-subscribed-table', rankings.most_subscribed, 'subscriberCount');
    }
    
    // Most Viewed
    if (rankings.most_viewed) {
        populateRankingTable('most-viewed-table', rankings.most_viewed, 'viewCount');
    }
    
    // Most Videos
    if (rankings.most_videos) {
        populateRankingTable('most-videos-table', rankings.most_videos, 'videoCount');
    }
    
    // Least Subscribed
    if (rankings.least_subscribed) {
        populateLeastTable('least-subscribed-table', rankings.least_subscribed, ['subscriberCount', 'viewCount']);
    }
    
    // Least Viewed
    if (rankings.least_viewed) {
        populateLeastTable('least-viewed-table', rankings.least_viewed, ['viewCount', 'subscriberCount']);
    }
    
    // By Country
    if (rankings.by_country) {
        populateCountryTable(rankings.by_country);
    }
}

function populateRankingTable(tableId, data, primaryMetric) {
    const table = document.getElementById(tableId);
    if (!table || !data) return;
    
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = data.map((item, index) => {
        const rank = index + 1;
        const medal = rank <= 3 ? ['🥇', '🥈', '🥉'][rank - 1] : rank;
        
        return `
            <tr>
                <td><strong>${medal}</strong></td>
                <td>
                    <strong>${escapeHtml(item.title || 'Unknown')}</strong>
                </td>
                <td>${formatNumber(item.subscriberCount || 0)}</td>
                <td>${formatNumber(item.viewCount || 0)}</td>
                <td>${formatNumber(item.videoCount || 0)}</td>
                <td>${item.country || 'N/A'}</td>
                <td>
                    ${item.channelUrl ? 
                        `<a href="${item.channelUrl}" target="_blank" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-external-link-alt"></i>
                        </a>` : 
                        '-'}
                </td>
            </tr>
        `;
    }).join('');
}

function populateLeastTable(tableId, data, metrics) {
    const table = document.getElementById(tableId);
    if (!table || !data) return;
    
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = data.slice(0, 10).map(item => `
        <tr>
            <td><small>${escapeHtml(item.title || 'Unknown')}</small></td>
            ${metrics.map(metric => `<td><small>${formatNumber(item[metric] || 0)}</small></td>`).join('')}
        </tr>
    `).join('');
}

function populateCountryTable(data) {
    const table = document.getElementById('country-distribution-table');
    if (!table || !data) return;
    
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = data.map(item => `
        <tr>
            <td><strong>${item.country || 'Unknown'}</strong></td>
            <td>${formatNumber(item.channel_count || 0)}</td>
            <td>${formatNumber(item.total_subscribers || 0)}</td>
            <td>${formatNumber(item.total_views || 0)}</td>
        </tr>
    `).join('');
    
    // Create country chart
    createCountryChart(data.slice(0, 10));
}

function createAnalyticsCharts(videoStats) {
    if (!videoStats) return;
    
    // Query Distribution Chart
    if (videoStats.top_queries) {
        createQueryDistributionChart(videoStats.top_queries);
    }
    
    // Year Distribution Chart
    if (videoStats.videos_by_year) {
        createYearDistributionChart(videoStats.videos_by_year);
    }
}

function createQueryDistributionChart(topQueries) {
    const ctx = document.getElementById('queryDistributionChart');
    if (!ctx) return;
    
    const labels = topQueries.map(q => q.query);
    const data = topQueries.map(q => q.count);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Videos',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createYearDistributionChart(videosByYear) {
    const ctx = document.getElementById('yearDistributionChart');
    if (!ctx) return;
    
    const years = Object.keys(videosByYear).sort();
    const counts = years.map(year => videosByYear[year]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Videos Published',
                data: counts,
                fill: true,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createCountryChart(countryData) {
    const ctx = document.getElementById('countryChart');
    if (!ctx) return;
    
    const labels = countryData.map(c => c.country);
    const data = countryData.map(c => c.channel_count);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Load analytics when analysis page is shown
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for analysis page navigation
    const analysisLink = document.querySelector('[data-page="analysis"]');
    if (analysisLink) {
        analysisLink.addEventListener('click', function() {
            setTimeout(() => loadAdvancedAnalytics(), 100);
        });
    }
});
