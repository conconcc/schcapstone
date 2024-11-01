$(document).ready(function() {
    function updateData() {
        $.ajax({
            url: '/update',
            type: 'GET',
            success: function(response) {
                $('#data-table').empty();
                response.tables.forEach(function(table) {
                    $('#data-table').append(table);
                });
            },
            error: function(error) {
                console.log('Error:', error);
            }
        });
    }

    setInterval(updateData, 5000);

    // 페이지 로드 시 초기 데이터 업데이트
    updateData();
});