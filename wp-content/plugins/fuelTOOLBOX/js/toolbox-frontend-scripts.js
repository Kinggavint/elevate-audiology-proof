/**
 * Share links function
 * If user clicks link with class .share-link, it will share the link using navigator.share
 * Used by the new interactive map block's share quick links button and anything else using the .share-link class
 */
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', async (event) => {
        const link = event.target.closest('.share-link');
        if (!link) return;

        event.preventDefault();
        const { href: url } = link;
        const title = document.title;
        const text = `${title}`;

        if (navigator.share) {
            try {
                await navigator.share({ title, text, url });
                console.log("Content shared successfully!");
            } catch (error) {
                console.error("Error sharing:", error);
            }
        } else {
            alert(`Sharing is not supported on this browser. Copy the link manually: ${url}`);
        }
    });
});