import React from 'react';

export default function AboutLink() {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const element = document.getElementById('features');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      // If on another page, navigate to homepage with hash
      window.location.href = '/#features';
    }
  };

  return (
    <a
      href="/#features"
      className="navbar__item navbar__link"
      onClick={handleClick}
    >
      About
    </a>
  );
}
