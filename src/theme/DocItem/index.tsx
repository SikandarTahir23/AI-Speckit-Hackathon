/**
 * DocItem wrapper - Re-exports original component
 * Custom logic is in DocItem/Layout for proper doc context access
 */

import React from 'react';
import DocItem from '@theme-original/DocItem';
import type {Props} from '@theme/DocItem';

export default function DocItemWrapper(props: Props): JSX.Element {
  return <DocItem {...props} />;
}
