import React from 'react';
import { render } from './test-utils/test-utils';
import App from './App';

test('renders app without crashing', () => {
  const { container } = render(<App />);
  // Just check that the app renders without errors
  expect(container).toBeTruthy();
});