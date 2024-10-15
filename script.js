const linkGroups = [
    {
        name: "Socials",
        icon: "share",
        links: [
            { name: "LinkedIn", url: "https://www.linkedin.com/in/adamwanninger", icon: "business" },
            { name: "GitHub", url: "https://www.github.com/ajwann", icon: "code" }
        ]
    },
    {
        name: "Speaking",
        icon: "record_voice_over",
        links: [
            { name: "Product Coffee", url: "https://podcasts.apple.com/us/podcast/product-coffee/id1466136912?i=1000587734194", icon:"campaign" },
            { name: "OLF '21", url: "https://youtu.be/o5FHxT2E9Qo", icon: "campaign" }
        ]
    },
    {
        name: "Writing",
        icon: "edit_note",
        links: [
            { name: "Feature Flags for Product Managers: Give Yourself Options for Handling Risk", url: "https://hackernoon.com/feature-flags-for-product-managers-give-yourself-options-for-handling-risk", icon: "notes" },
            { name: "What's The Most Important Skill for a Senior Developer?", url: "https://hackernoon.com/most-important-skill-for-a-senior-developer-1d2d3zyg", icon: "notes" }
        ]
    },
    {
        name: "Reading",
        icon: "menu_book",
        links: [
            { name: "INSPIRED", url: "https://books.apple.com/us/book/inspired/id1400567600", icon: "book" },
            { name: "Escaping the Build Trap", url: "https://books.apple.com/us/audiobook/escaping-the-build-trap-how-effective-product/id1642646989", icon: "book" },
            { name: "TRANSFORMED", url: "https://books.apple.com/us/audiobook/transformed-moving-to-the-product-operating-model/id1710321644", icon: "book" },
            { name: "EMPOWERED", url: "https://books.apple.com/us/audiobook/empowered-ordinary-people-extraordinary-products/id1648996249", icon: "book" },
            { name: "Measure What Matters", url: "https://books.apple.com/us/audiobook/measure-what-matters-how-google-bono-and-the/id1416417939", icon: "book" }
        ]
    },
    {
        name: "Contact",
        icon: "contact_mail",
        links: [
            { name: "Email", url: "mailto:adam@awanninger.com", icon: "email" }
        ]
    }
];

const linksContainer = document.getElementById("links");

linkGroups.forEach((group, index) => {
    const linkGroup = document.createElement("div");
    linkGroup.className = "link-group";

    const button = document.createElement("div");
    button.className = "link-button";
    button.innerHTML = `<i class="material-icons">${group.icon}</i>${group.name}`;
    button.addEventListener("click", () => toggleLinkList(index));

    const linkList = document.createElement("ul");
    linkList.className = "link-list";
    linkList.id = `link-list-${index}`;

    group.links.forEach(link => {
        const linkItem = document.createElement("li");
        linkItem.className = "link-item";
        linkItem.innerHTML = `<a href="${link.url}" target="_blank"><i class="material-icons">${link.icon}</i>${link.name}</a>`;
        linkList.appendChild(linkItem);
    });

    linkGroup.appendChild(button);
    linkGroup.appendChild(linkList);
    linksContainer.appendChild(linkGroup);
});

function toggleLinkList(index) {
    const linkList = document.getElementById(`link-list-${index}`);
    linkList.classList.toggle("active");
}
