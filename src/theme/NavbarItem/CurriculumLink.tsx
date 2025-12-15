import React from 'react';

export default function CurriculumLink() {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const element = document.getElementById('chapters');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      // If on another page, navigate to homepage with hash
      window.location.href = '/#chapters';
    }
  };

  return (
    <a
      href="/#chapters"
      className="navbar__item navbar__link"
      onClick={handleClick}
    >
      Curriculum
    </a>
  );
}
