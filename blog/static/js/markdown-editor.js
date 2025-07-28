// blog/static/js/markdown-editor.js

document.addEventListener('DOMContentLoaded', function() {
    // Find all textareas with the 'markdown-editor' class
    const editors = document.querySelectorAll('.markdown-editor');

    editors.forEach(function(editor) {
        // Initialize EasyMDE for each textarea
        new EasyMDE({
            element: editor,
            spellChecker: true, // Optional: disable spell checker
            status: ["lines", "words"], // Optional: show line and word count in the status bar
            toolbar: [
                "bold", "italic", "heading", "|",
                "quote", "unordered-list", "ordered-list", "|",
                "link", "image", "|",
                "preview", "side-by-side", "fullscreen", "|",
                "guide"
            ],
            // NEW: Prevent side-by-side mode from going fullscreen
            sideBySideFullscreen: false,
            indentWithTabs: false,
            tabSize: 4,
            unorderedListStyle: "*",
            // Enable the syntax highlighting feature
            renderingConfig: {
                codeSyntaxHighlighting: true,
            }
        });
    });
});