/* =========================================================
   FocusFinance — script.js
   Handles mobile navigation, flash-message auto-dismiss,
   client-side form validation helpers, and dark mode toggle.
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {

    /* -----------------------------------------------------
       Mobile hamburger menu toggle
    ----------------------------------------------------- */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function () {
            navLinks.classList.toggle('show');
        });
    }

    /* -----------------------------------------------------
       Auto-dismiss flash messages after 5 seconds
    ----------------------------------------------------- */
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    /* -----------------------------------------------------
       Signup form: client-side password match check
    ----------------------------------------------------- */
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function (e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match. Please re-check.');
                return false;
            }

            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long.');
                return false;
            }
        });
    }

    /* -----------------------------------------------------
       Mobile number validation (10 digits) for any form
       that includes a "mobile" input
    ----------------------------------------------------- */
    const mobileInputs = document.querySelectorAll('input[name="mobile"]');
    mobileInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    });

    /* -----------------------------------------------------
       Eligibility / Apply forms: simple numeric guard
       (prevents negative numbers being typed in number fields)
    ----------------------------------------------------- */
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    /* -----------------------------------------------------
       Smooth scroll for in-page anchor links (if any)
    ----------------------------------------------------- */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    /* -----------------------------------------------------
       Dark Mode Toggle
    ----------------------------------------------------- */
    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        themeToggleBtn.textContent = currentTheme === 'dark' ? '☀️' : '🌙';

        themeToggleBtn.addEventListener('click', function () {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (isDark) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                themeToggleBtn.textContent = '🌙';
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggleBtn.textContent = '☀️';
            }
        });
    }

});