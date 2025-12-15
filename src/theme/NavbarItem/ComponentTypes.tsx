import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import LoginButton from './LoginButton';
import AboutLink from './AboutLink';
import CurriculumLink from './CurriculumLink';
import ColorModeToggle from './ColorModeToggle';
import BookLink from './BookLink';

export default {
  ...ComponentTypes,
  'custom-login': LoginButton,
  'custom-about': AboutLink,
  'custom-curriculum': CurriculumLink,
  'custom-color-toggle': ColorModeToggle,
  'custom-book': BookLink,
};
