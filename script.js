const linkGroups = [
    {
        name: "Social Media",
        icon: "share",
        links: [
            { name: "LinkedIn", url: "https://www.linkedin.com/in/adamwanninger", icon: "business" },
            { name: "GitHub", url: "https://www.github.com/ajwann", icon: "code" }
        ]
    },
    {
        name: "Speaking",
        icon: "work",
        links: [
            { name: "Product Coffee", url: "https://podcasts.apple.com/us/podcast/product-coffee/id1466136912?i=1000587734194", icon: "business" },
            { name: "OLF '21", url: "https://youtu.be/o5FHxT2E9Qo", icon: "code" }
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
