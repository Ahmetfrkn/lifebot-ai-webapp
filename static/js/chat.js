$(document).ready(function () {
    $('#chatForm').on('submit', function (e) {
        e.preventDefault();

        const mesaj = $('textarea[name="metin"]').val().trim();
        if (!mesaj) return;

        $('textarea[name="metin"]').val("");
        scrollToBottom();

        $.ajax({
            url: "/api/chat",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                mesaj: mesaj,
                sohbet_id: secili_sohbet_id
            }),
            success: function (response) {
                if (response.cevap) {
                    const botMessage = `<div class="chat-bubble bot">${response.cevap}</div>`;
                    $('.chat-display').append(botMessage);
                    scrollToBottom();
                }
            },
            error: function () {
                const hata = `<div class="chat-bubble bot" style="background:#f8d7da;color:#721c24;">Sunucu hatası oluştu.</div>`;
                $('.chat-display').append(hata);
                scrollToBottom();
            }
        });
    });

    function scrollToBottom() {
        const chatDisplay = document.getElementById("chat-display");
        if (chatDisplay)
            chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
});
