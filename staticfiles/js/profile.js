document.addEventListener('DOMContentLoaded', function() {
    // CSRF token'ı al
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Profil fotoğrafı yükleme
    const profilePictureInput = document.getElementById('profile_picture');
    const profilePicturePreview = document.getElementById('profile_picture_preview');
    const currentProfilePicture = document.getElementById('current_profile_picture');

    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicturePreview.src = e.target.result;
                    profilePicturePreview.style.display = 'block';
                    if (currentProfilePicture) {
                        currentProfilePicture.style.display = 'none';
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Profil düzenleme formu
    const profileForm = document.getElementById('profile_form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Başarılı!',
                        text: 'Profiliniz başarıyla güncellendi.',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Hata!',
                        text: data.message || 'Bir hata oluştu.',
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Hata!',
                    text: 'Bir hata oluştu. Lütfen tekrar deneyin.',
                });
            });
        });
    }

    // Mesajları otomatik kapat
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 3000);
    });

    // Yanıt düzenleme butonları için event listener
    document.querySelectorAll('.edit-response-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const responseId = this.dataset.responseId;
            const responseText = this.dataset.responseText;

            Swal.fire({
                title: 'Yanıtı Düzenle',
                html: `<textarea id="response_text" class="form-control" rows="4">${responseText}</textarea>`,
                showCancelButton: true,
                confirmButtonText: 'Kaydet',
                cancelButtonText: 'İptal',
                preConfirm: () => {
                    const newText = document.getElementById('response_text').value;
                    if (!newText.trim()) {
                        Swal.showValidationMessage('Lütfen yanıt alanını doldurun');
                        return false;
                    }
                    return { response_text: newText };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/response/${responseId}/edit/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': csrfToken
                        },
                        body: `response_text=${encodeURIComponent(result.value.response_text)}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            window.location.reload();
                        } else {
                            Swal.fire('Hata!', data.message || 'Bir hata oluştu', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Hata!', 'Bir hata oluştu', 'error');
                    });
                }
            });
        });
    });

    // Yanıt silme butonları için event listener
    document.querySelectorAll('.delete-response-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const responseId = this.dataset.responseId;

            Swal.fire({
                title: 'Emin misiniz?',
                text: 'Bu yanıtı silmek istediğinizden emin misiniz?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Evet, Sil',
                cancelButtonText: 'İptal'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/response/${responseId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            window.location.reload();
                        } else {
                            Swal.fire('Hata!', data.message || 'Bir hata oluştu', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Hata!', 'Bir hata oluştu', 'error');
                    });
                }
            });
        });
    });
}); 