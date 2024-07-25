const links = [
    { name: "Website", url: "https://yourwebsite.com", icon: "language" },
    { name: "GitHub", url: "https://github.com/yourusername", icon: "code" },
    { name: "LinkedIn", url: "https://linkedin.com/in/yourusername", icon: "work" },
    { name: "Twitter", url: "https://twitter.com/yourusername", icon: "chat" }
];

const linksContainer = document.getElementById("links");

links.forEach(link => {
    const linkElement = document.createElement("a");
    linkElement.href = link.url;
    linkElement.className = "link";
    linkElement.innerHTML = `<i class="material-icons">${link.icon}</i>${link.name}`;
    linkElement.target = "_blank";
    linksContainer.appendChild(linkElement);
});
