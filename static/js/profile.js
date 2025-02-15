document.addEventListener('DOMContentLoaded', function() {
    // Mesaj otomatik kapatma
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Yorum silme onayı
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Bu yorumu silmek istediğinizden emin misiniz?')) {
                e.preventDefault();
            }
        });
    });

    // Profil fotoğrafı önizleme
    const profilePictureInput = document.querySelector('input[name="profile_picture"]');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const profileImg = document.querySelector('.profile-img');
                    if (profileImg) {
                        profileImg.src = e.target.result;
                    } else {
                        const defaultAvatar = document.querySelector('.default-avatar');
                        if (defaultAvatar) {
                            defaultAvatar.innerHTML = `<img src="${e.target.result}" class="profile-img">`;
                        }
                    }
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}); 