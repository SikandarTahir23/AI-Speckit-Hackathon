import React from 'react';
import Link from '@docusaurus/Link';

export default function BookLink() {
  return (
    <Link
      to="/docs/chapter-1-introduction-to-physical-ai"
      className="navbar__item navbar__link"
    >
      Chapters
    </Link>
  );
}
