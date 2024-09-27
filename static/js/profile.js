document.addEventListener('DOMContentLoaded', function() {
    const usernameText = document.getElementById('usernameText');
    const usernameInput = document.getElementById('usernameInput');
    const editUsernameBtn = document.getElementById('editUsername');
    const passwordText = document.getElementById('passwordText');
    const passwordInput = document.getElementById('passwordInput');
    const editPasswordBtn = document.getElementById('editPassword');
    const updateProfileBtn = document.getElementById('updateProfile');

    let isEditingUsername = false;
    let isEditingPassword = false;

    function toggleEdit(textElement, inputElement, editBtn, isEditing) {
        if (isEditing) {
            textElement.classList.add('hidden');
            inputElement.classList.remove('hidden');
            editBtn.textContent = 'Cancel';
            updateProfileBtn.classList.remove('hidden');
        } else {
            textElement.classList.remove('hidden');
            inputElement.classList.add('hidden');
            editBtn.textContent = 'Edit';
            if (!isEditingUsername && !isEditingPassword) {
                updateProfileBtn.classList.add('hidden');
            }
        }
    }

    editUsernameBtn.addEventListener('click', function() {
        isEditingUsername = !isEditingUsername;
        toggleEdit(usernameText, usernameInput, editUsernameBtn, isEditingUsername);
    });

    editPasswordBtn.addEventListener('click', function() {
        isEditingPassword = !isEditingPassword;
        toggleEdit(passwordText, passwordInput, editPasswordBtn, isEditingPassword);
    });

    updateProfileBtn.addEventListener('click', function() {
        const username = usernameInput.value;
        const password = passwordInput.value;

        fetch('/api/profile/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Profile updated successfully!');
                usernameText.textContent = username;
                passwordInput.value = '';
                isEditingUsername = false;
                isEditingPassword = false;
                toggleEdit(usernameText, usernameInput, editUsernameBtn, isEditingUsername);
                toggleEdit(passwordText, passwordInput, editPasswordBtn, isEditingPassword);
            } else {
                alert('Failed to update profile: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while updating the profile.');
        });
    });
});