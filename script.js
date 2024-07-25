const linkGroups = [
    {
        name: "Social Media",
        icon: "share",
        links: [
            { name: "Twitter", url: "https://twitter.com/yourusername", icon: "chat" },
            { name: "Instagram", url: "https://instagram.com/yourusername", icon: "camera_alt" },
            { name: "Facebook", url: "https://facebook.com/yourusername", icon: "thumb_up" }
        ]
    },
    {
        name: "Professional",
        icon: "work",
        links: [
            { name: "LinkedIn", url: "https://linkedin.com/in/yourusername", icon: "business" },
            { name: "GitHub", url: "https://github.com/yourusername", icon: "code" },
            { name: "Portfolio", url: "https://yourportfolio.com", icon: "web" }
        ]
    },
    {
        name: "Contact",
        icon: "contact_mail",
        links: [
            { name: "Email", url: "mailto:your.email@example.com", icon: "email" },
            { name: "Phone", url: "tel:+1234567890", icon: "phone" }
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
