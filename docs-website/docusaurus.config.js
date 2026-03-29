module.exports = {
  title: "DataHub 한국어 문서",
  tagline: "메타데이터 관리 플랫폼 한국어 문서",
  url: "https://yoon-gu.github.io",
  baseUrl: "/datahub/",
  onBrokenLinks: "ignore",
  onBrokenMarkdownLinks: "ignore",
  favicon: "img/favicon.ico",
  organizationName: "yoon-gu",
  projectName: "datahub",
  staticDirectories: ["static"],
  markdown: {
    format: "md",
    mermaid: false,
  },
  i18n: {
    defaultLocale: "ko",
    locales: ["ko"],
  },
  themeConfig: {
    colorMode: {
      defaultMode: "light",
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "DataHub 문서",
      logo: {
        alt: "DataHub Logo",
        src: "img/datahub-logo-color-light-horizontal.svg",
      },
      items: [
        {
          to: "/docs",
          activeBasePath: "docs",
          label: "문서",
          position: "left",
        },
        {
          href: "https://github.com/yoon-gu/datahub",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "문서",
          items: [
            { label: "핵심 개념", to: "docs/what-is-datahub/datahub-concepts" },
            { label: "아키텍처", to: "docs/architecture/architecture" },
            { label: "Lineage", to: "docs/features/feature-guides/lineage" },
          ],
        },
        {
          title: "참고",
          items: [
            { label: "DataHub 공식 문서", href: "https://docs.datahub.com" },
            { label: "DataHub GitHub", href: "https://github.com/datahub-project/datahub" },
            { label: "DataHub 데모", href: "https://demo.datahub.com" },
          ],
        },
      ],
      copyright: `DS3실 내부 참고용 · ${new Date().getFullYear()}`,
    },
    prism: {
      additionalLanguages: ["java", "graphql", "bash", "yaml", "json"],
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          path: "genDocs",
          sidebarPath: require.resolve("./sidebars.js"),
          numberPrefixParser: false,
          showLastUpdateAuthor: false,
          showLastUpdateTime: false,
          remarkPlugins: [],
          rehypePlugins: [],
        },
        blog: false,
        theme: {},
        pages: {
          path: "src/pages",
        },
      },
    ],
  ],
};
