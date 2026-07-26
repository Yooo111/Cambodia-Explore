document.addEventListener("DOMContentLoaded", () => {
    const pwd = document.querySelector('input[name="password"]');
    if (!pwd) return;

    pwd.addEventListener("input", () => {
        const msg = document.querySelector("#passwordHelp");
        if (!msg) return;

        const v = pwd.Value;
        const strong =
        v.length >=8 &&
        /[A_Z]/.test(v) &&
        /[a-z]/.test(v) &&
        /[0-9]/.test(v) &&
        /[!@#$%^&*()=+-{}.,<>?:]/.test(v);

        msg.textContent = strong
            ? "Strong password🔐"
            : "Use at least 8 chars, with upper, lower, number, and special symbol.";
        msg.className = strong ? "form-text text-success" : "form-text text-danger";
    });
});