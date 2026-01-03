document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('scoreChart');
    if (!ctx) return;

    // 1. Lấy dữ liệu điểm và ngày từ HTML truyền sang
    const chartData = (typeof SERVER_SCORE_LIST !== 'undefined' && SERVER_SCORE_LIST.length > 0) 
                      ? SERVER_SCORE_LIST 
                      : [0];
                      
    const chartLabels = (typeof SERVER_DATE_LIST !== 'undefined' && SERVER_DATE_LIST.length > 0)
                      ? SERVER_DATE_LIST
                      : ['Không có dữ liệu'];

    // 2. Khởi tạo Chart.js
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels, // Bây giờ nhãn sẽ là ngày tháng (YYYY-MM-DD)
            datasets: [{
                label: 'Điểm số',
                data: chartData,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderWidth: 3,
                tension: 0.3, 
                fill: true,
                pointRadius: 5,
                pointBackgroundColor: '#0d6efd',
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { stepSize: 2 }
                },
                x: {
                    grid: { display: false },
                    ticks: {
                        maxRotation: 45, // Xoay ngày tháng một chút nếu bị khít nhau
                        minRotation: 45,
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return 'Ngày: ' + context[0].label;
                        },
                        label: function(context) {
                            return ' Điểm: ' + context.parsed.y + '/10';
                        }
                    }
                }
            }
        }
    });
});