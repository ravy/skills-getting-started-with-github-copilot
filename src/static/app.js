document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Reset activity select options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants title
        const participantsTitle = document.createElement('p');
        participantsTitle.innerHTML = '<strong>Participants:</strong>';
        activityCard.appendChild(participantsTitle);

        if (details.participants && details.participants.length > 0) {
          const ul = document.createElement('ul');
          ul.className = 'participants-list';

          details.participants.forEach((participant) => {
            const li = document.createElement('li');
            li.className = 'participant-item';

            const span = document.createElement('span');
            span.textContent = participant;

            const btn = document.createElement('button');
            btn.className = 'remove-btn';
            btn.title = 'Unregister participant';
            btn.textContent = '✖';

            btn.addEventListener('click', async () => {
              try {
                const resp = await fetch(`/activities/${encodeURIComponent(name)}/participants?email=${encodeURIComponent(participant)}`, {
                  method: 'DELETE',
                });

                const resJson = await resp.json();
                if (resp.ok) {
                  messageDiv.textContent = resJson.message;
                  messageDiv.className = 'success';
                  // refresh activities list
                  fetchActivities();
                } else {
                  messageDiv.textContent = resJson.detail || 'Failed to unregister';
                  messageDiv.className = 'error';
                }

                messageDiv.classList.remove('hidden');
                setTimeout(() => {
                  messageDiv.classList.add('hidden');
                }, 5000);
              } catch (error) {
                messageDiv.textContent = 'Failed to unregister. Please try again.';
                messageDiv.className = 'error';
                messageDiv.classList.remove('hidden');
                console.error('Error unregistering:', error);
              }
            });

            li.appendChild(span);
            li.appendChild(btn);
            ul.appendChild(li);
          });

          activityCard.appendChild(ul);
        } else {
          const p = document.createElement('p');
          p.className = 'info';
          p.textContent = 'No participants yet.';
          activityCard.appendChild(p);
        }

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // refresh activities list so the new participant appears immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
