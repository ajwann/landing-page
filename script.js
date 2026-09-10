const linkGroups = [
    {
        name: "About",
        icon: "person",
        html: `
            <p>I'm a technology leader with a background in product management, the kind of PM who
            still reads the diff. Today I spend my time helping teams build software worth using; before
            that, I shipped it myself.</p>
            <p>I began my career as a proud member of the Ruby on Rails community, and it shaped how I
            think about craft, convention, and welcoming newcomers.</p>
        `
    },
    {
        name: "Connect",
        icon: "share",
        links: [
            { name: "LinkedIn", url: "https://www.linkedin.com/in/adamwanninger", icon: "business" },
            { name: "GitHub", url: "https://www.github.com/ajwann", icon: "code" },
            { name: "Email", url: "mailto:adam@awanninger.com", icon: "email" }
        ]
    },
    {
        name: "Open Source",
        icon: "commit",
        links: [
            { name: "cats-mcp: an MCP server for live Charlotte Area Transit bus and rail data", url: "https://github.com/ajwann/cats-mcp", icon: "directions_bus", badge: "New" },
            { name: "svg-loaders-react: React adaptation of the SVG Loaders library", url: "https://github.com/ajwann/svg-loaders-react", icon: "star" },
            { name: "RubyGems and Bundler: 18 commits, including a bundle bin path fix and a proper PathError", url: "https://github.com/ruby/rubygems/commits?author=ajwann", icon: "code" },
            { name: "ruby/ruby: a commit of mine in the Ruby language repo", url: "https://github.com/ruby/ruby/commit/aad7443e168880e382680d4c0be1757840b23c18", icon: "diamond" },
            { name: "exercism.io: test generators for the Ruby track", url: "https://github.com/exercism/ruby/commits?author=ajwann", icon: "school" }
        ]
    },
    {
        name: "Talks",
        icon: "record_voice_over",
        links: [
            { name: "Product Coffee", url: "https://podcasts.apple.com/us/podcast/product-coffee/id1466136912?i=1000587734194", icon:"campaign" },
            { name: "OLF '21", url: "https://youtu.be/o5FHxT2E9Qo", icon: "campaign" }
        ]
    },
    {
        name: "Articles",
        icon: "edit_note",
        links: [
            { name: "Feature Flags for Product Managers: Give Yourself Options for Handling Risk", url: "https://hackernoon.com/feature-flags-for-product-managers-give-yourself-options-for-handling-risk", icon: "notes" },
            { name: "What's The Most Important Skill for a Senior Developer?", url: "https://hackernoon.com/most-important-skill-for-a-senior-developer-1d2d3zyg", icon: "notes" }
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

    if (group.html) {
        const bioItem = document.createElement("li");
        bioItem.className = "link-item bio";
        bioItem.innerHTML = group.html;
        linkList.appendChild(bioItem);
    }

    (group.links || []).forEach(link => {
        const linkItem = document.createElement("li");
        linkItem.className = link.badge ? "link-item featured" : "link-item";
        const badge = link.badge ? `<span class="badge">${link.badge}</span>` : "";
        linkItem.innerHTML = `<a href="${link.url}" target="_blank"><i class="material-icons">${link.icon}</i>${link.name}${badge}</a>`;
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
