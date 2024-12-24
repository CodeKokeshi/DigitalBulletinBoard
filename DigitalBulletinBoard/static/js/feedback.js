document.getElementById('feedback-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('feedback-title').value;
    const description = document.getElementById('feedback-description').value;
    const attachment = document.getElementById('feedback-attachment').files[0];

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    if (attachment) {
        formData.append('attachment', attachment);
    }

    const response = await fetch('/submit_feedback', {
        method: 'POST',
        body: formData,
    });

    const feedbackModal = new bootstrap.Modal(document.getElementById('feedbackModal'));
    const feedbackModalBody = document.getElementById('feedbackModalBody');
    const modalOkButton = document.getElementById('modal-ok-button');

    if (response.ok) {
        feedbackModalBody.textContent = 'Feedback submitted successfully.';
        modalOkButton.onclick = () => window.close();
    } else {
        feedbackModalBody.textContent = 'Failed to submit feedback.';
        modalOkButton.onclick = () => location.reload();
    }

    feedbackModal.show();
});