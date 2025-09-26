#!/usr/bin/env python3
#encoding=utf-8
# seleniumwire not support python 2.x.
# if you want running under python 2.x, you need to assign driver_type = 'stealth'
import os
import pathlib
import sys
import platform
import json
import random
import base64
import inspect
import asyncio
import threading
import re
from typing import Any, List, Optional

# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    from selenium.webdriver.support.ui import Select as SeleniumSelect
except ImportError:  # pragma: no cover - optional dependency
    SeleniumSelect = None
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
# for selenium 4
from selenium.webdriver.chrome.service import Service
# for wait #1
import time
# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import argparse
import chromedriver_autoinstaller

try:  # pragma: no cover - optional dependency
    from DrissionPage import ChromiumOptions, ChromiumPage
    from DrissionPage._elements.chromium_element import (
        ChromiumElement as _ChromiumElement,
    )
    from DrissionPage._pages.chromium_frame import ChromiumFrame as _ChromiumFrame
except Exception:  # pragma: no cover - optional dependency
    ChromiumOptions = None
    ChromiumPage = None
    _ChromiumElement = None
    _ChromiumFrame = None

try:
    import nodriver
    from nodriver import cdp
    try:  # pragma: no cover - optional dependency
        from nodriver.core import element as nodriver_core_element
        from nodriver.core import util as nodriver_util
    except Exception:  # pragma: no cover - defensive fallback
        nodriver_core_element = None
        nodriver_util = None
except ImportError:  # pragma: no cover - optional dependency
    nodriver = None
    cdp = None
    nodriver_core_element = None
    nodriver_util = None

_CHROMEDRIVER_INSTALL_SUPPORTS_VERSION_DIR = "make_version_dir" in inspect.signature(
    chromedriver_autoinstaller.install
).parameters


def install_chromedriver_binary(webdriver_path):
    install_kwargs = {"path": webdriver_path}
    if _CHROMEDRIVER_INSTALL_SUPPORTS_VERSION_DIR:
        install_kwargs["make_version_dir"] = False
    chromedriver_autoinstaller.install(**install_kwargs)

CONST_APP_VERSION = "Max inline Bot (2023.08.21)"

CONST_MAXBOT_CONFIG_FILE = 'settings.json'
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"

CONST_HOMEPAGE_DEFAULT = "https://inline.app/zh/?language=zh-tw"
URL_CHROME_DRIVER = "https://chromedriver.chromium.org/downloads"

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"
CONST_WEBDRIVER_TYPE_DRISSION = "drissionpage"


class Keys:
    ENTER = "\r"
    END = "\uE010"


if nodriver is not None:

    class NodriverElement:
        def __init__(self, session: "NodriverWebDriver", element: "nodriver.Element"):
            self._session = session
            self._element = element

        def __bool__(self) -> bool:
            return self._element is not None

        def __repr__(self) -> str:  # pragma: no cover - debugging helper
            return f"<NodriverElement tag={self.tag_name}>"

        @property
        def tag_name(self) -> str:
            return (self._element.node.node_name or "").lower()

        def click(self) -> None:
            self._session._run(self._element.click())

        def clear(self) -> None:
            try:
                self._session._run(self._element.clear_input())
            except Exception:
                self._session._run(
                    self._element.apply("(elem) => { elem.value = ''; }")
                )

        def find_element(self, by: str, value: str) -> "NodriverElement":
            return self._session._find_element(by, value, base=self)

        def find_elements(self, by: str, value: str) -> List["NodriverElement"]:
            return self._session._find_elements(by, value, base=self)

        def get_attribute(self, name: str) -> Optional[str]:
            escaped = name.replace("'", "\\'")
            prop_name = json.dumps(name)
            script = (
                "(elem) => {"
                f"  const attr = elem.getAttribute('{escaped}');"
                "  if (attr !== null) { return attr; }"
                f"  const prop = elem[{prop_name}];"
                "  if (prop === undefined || prop === null) { return null; }"
                "  return String(prop);"
                "}"
            )
            result = self._session._run(self._element.apply(script))
            if result is None:
                return None
            return str(result)

        def is_selected(self) -> bool:
            result = self._session._run(
                self._element.apply(
                    "(elem) => Boolean(elem.checked ?? elem.selected ?? false)"
                )
            )
            return bool(result)

        def is_displayed(self) -> bool:
            script = """
                (elem) => {
                  if (!elem || !(elem instanceof Element)) {
                    return false;
                  }
                  if (elem.hasAttribute && elem.hasAttribute('hidden')) {
                    return false;
                  }
                  const style = window.getComputedStyle(elem);
                  if (!style) {
                    return false;
                  }
                  if (style.display === 'none' || style.visibility === 'hidden' || style.visibility === 'collapse') {
                    return false;
                  }
                  if (style.pointerEvents === 'none') {
                    return false;
                  }
                  const rect = elem.getBoundingClientRect();
                  const hasSize = rect && (rect.width !== 0 || rect.height !== 0);
                  if (!hasSize && elem.getClientRects().length === 0) {
                    return false;
                  }
                  const ariaHidden = elem.getAttribute && elem.getAttribute('aria-hidden');
                  if (ariaHidden && ariaHidden.toLowerCase() === 'true') {
                    return false;
                  }
                  let current = elem;
                  while (current) {
                    if (current.hasAttribute && current.hasAttribute('hidden')) {
                      return false;
                    }
                    const root = current.getRootNode && current.getRootNode();
                    current = current.parentElement || (root && root.host) || null;
                  }
                  return true;
                }
            """
            result = self._session._run(self._element.apply(script))
            return bool(result)

        def is_enabled(self) -> bool:
            script = """
                (elem) => {
                  if (!elem || !(elem instanceof Element)) {
                    return false;
                  }
                  if (elem.disabled) {
                    return false;
                  }
                  if (elem.hasAttribute && elem.hasAttribute('disabled')) {
                    return false;
                  }
                  const ariaDisabled = elem.getAttribute && elem.getAttribute('aria-disabled');
                  if (ariaDisabled && ariaDisabled.toLowerCase() === 'true') {
                    return false;
                  }
                  const fieldset = elem.closest ? elem.closest('fieldset') : null;
                  if (fieldset && fieldset.disabled) {
                    return false;
                  }
                  const style = window.getComputedStyle(elem);
                  if (style && style.pointerEvents === 'none') {
                    return false;
                  }
                  return true;
                }
            """
            result = self._session._run(self._element.apply(script))
            return bool(result)

        @property
        def text(self) -> str:
            result = self._session._run(
                self._element.apply("(elem) => elem.innerText ?? ''")
            )
            if result is None:
                return ""
            return str(result)

        def send_keys(self, value: Any) -> None:
            text = self._session._format_keys(value)
            if text:
                self._session._run(self._element.send_keys(text))


    class NodriverAlert:
        def __init__(self, session: "NodriverWebDriver"):
            self._session = session

        def accept(self) -> None:
            self._session._run(
                self._session._active_tab.send(
                    cdp.page.handle_java_script_dialog(accept=True)
                )
            )

        def dismiss(self) -> None:
            self._session._run(
                self._session._active_tab.send(
                    cdp.page.handle_java_script_dialog(accept=False)
                )
            )


    class NodriverSwitchTo:
        def __init__(self, session: "NodriverWebDriver"):
            self._session = session

        def window(self, handle: str) -> None:
            self._session._switch_window(handle)

        def frame(self, frame_reference: NodriverElement) -> None:
            if not isinstance(frame_reference, NodriverElement):
                raise TypeError("frame reference must be a NodriverElement")
            self._session._frame_stack.append(frame_reference)

        def default_content(self) -> None:
            self._session._frame_stack.clear()

        @property
        def alert(self) -> NodriverAlert:
            return NodriverAlert(self._session)


    class NodriverSelect:
        def __init__(self, element: NodriverElement):
            if element.tag_name != "select":
                raise ValueError("NodriverSelect only supports <select> elements")
            self._element = element

        def _dispatch_change(self) -> None:
            self._element._session._run(
                self._element._element.apply(
                    "(elem) => { elem.dispatchEvent(new Event('input', {bubbles: true}));"
                    " elem.dispatchEvent(new Event('change', {bubbles: true})); }"
                )
            )

        def select_by_value(self, value: str) -> None:
            escaped = value.replace("'", "\\'")
            script = (
                "(elem) => {"
                f"  const options = Array.from(elem.options || []);"
                f"  const target = options.find(opt => opt.value === '{escaped}');"
                "  if (target) { elem.value = target.value; return true; }"
                "  return false;"
                "}"
            )
            success = self._element._session._run(
                self._element._element.apply(script)
            )
            if not success:
                raise NoSuchElementException(
                    f"Cannot locate option with value: {value}"
                )
            self._dispatch_change()

        def select_by_visible_text(self, text: str) -> None:
            escaped = text.replace("'", "\\'")
            script = (
                "(elem) => {"
                "  const options = Array.from(elem.options || []);"
                f"  const target = options.find(opt => (opt.textContent || '').trim() === '{escaped}');"
                "  if (target) { elem.value = target.value; return true; }"
                "  return false;"
                "}"
            )
            success = self._element._session._run(
                self._element._element.apply(script)
            )
            if not success:
                raise NoSuchElementException(
                    f"Cannot locate option with text: {text}"
                )
            self._dispatch_change()


    class NodriverWebDriver:
        def __init__(self, config_dict: dict):
            if nodriver is None:
                raise RuntimeError("nodriver is not installed")

            self._config = config_dict
            self._loop = asyncio.new_event_loop()
            self._loop_thread = threading.Thread(
                target=self._loop.run_forever, daemon=True
            )
            self._loop_thread.start()
            self._frame_stack: List[NodriverElement] = []
            self._script_timeout = None
            self.switch_to = NodriverSwitchTo(self)

            browser_args = self._build_browser_args()
            headless = bool(config_dict.get("advanced", {}).get("headless", False))
            browser_path = None
            if config_dict.get("browser") == "brave":
                brave_path = get_brave_bin_path()
                if os.path.exists(brave_path):
                    browser_path = brave_path

            lang = "zh-TW"
            try:
                lang = config_dict.get("language", "zh-TW")
            except Exception:
                pass

            self._browser = self._run(
                nodriver.start(
                    headless=headless,
                    browser_executable_path=browser_path,
                    browser_args=browser_args,
                    lang=lang,
                )
            )
            self._active_tab = self._browser.main_tab
            self._handles: List[str] = []
            self._refresh_handles()

        # ------------------------------------------------------------------
        # helpers
        # ------------------------------------------------------------------
        def _run(self, coro: "asyncio.Future"):
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return future.result()

        def _build_browser_args(self) -> List[str]:
            args = [
                "--disable-features=TranslateUI",
                "--disable-translate",
                "--disable-web-security",
                "--no-sandbox",
                "--password-store=basic",
            ]
            if not self._config.get("advanced", {}).get("headless", False):
                args.append("--start-maximized")
            return args

        def _refresh_handles(self) -> None:
            self._handles = []
            for tab in self._browser.tabs:
                if tab.target:
                    self._handles.append(tab.target.target_id)
            if self._active_tab and self._active_tab.target:
                active_handle = self._active_tab.target.target_id
                if active_handle not in self._handles and self._handles:
                    self._switch_window(self._handles[0])

        def _switch_window(self, handle: str) -> None:
            for tab in self._browser.tabs:
                if tab.target and tab.target.target_id == handle:
                    self._active_tab = tab
                    self._frame_stack.clear()
                    return
            raise NoSuchWindowException(f"No window with handle {handle}")

        def _current_context(self, base: Optional[NodriverElement] = None):
            if base is not None:
                return base._element
            if self._frame_stack:
                return self._frame_stack[-1]._element
            return None

        def _selector_from(self, by: str, value: str) -> str:
            if by == By.ID:
                return f"#{value}"
            if by == By.CSS_SELECTOR:
                return value
            if by == By.NAME:
                return f"[name='{value}']"
            if by == By.CLASS_NAME:
                classes = ".".join(part for part in value.split() if part)
                return f".{classes}" if classes else value
            if by == By.TAG_NAME:
                return value
            if by == By.XPATH:
                return self._convert_xpath(value)
            raise NotImplementedError(f"By strategy {by} is not supported in nodriver mode")

        def _convert_xpath(self, xpath: str) -> str:
            pattern = r"//(?P<tag>\w+)\[@(?P<attr>[\w:-]+)='(?P<value>[^']*)'\](?P<suffix>/.*)?"
            match = re.fullmatch(pattern, xpath)
            if not match:
                raise NotImplementedError(f"Unsupported XPath in nodriver mode: {xpath}")
            selector = f"{match.group('tag')}[{match.group('attr')}='{match.group('value')}']"
            suffix = match.group("suffix")
            if suffix:
                suffix = suffix.lstrip("/")
                if suffix:
                    selector += " " + " ".join(filter(None, suffix.split("/")))
            return selector

        async def _query_selector(self, selector: str, base: Optional[NodriverElement] = None):
            context = self._current_context(base)
            if context is not None:
                result = await context.query_selector(selector)
            else:
                result = await self._active_tab.query_selector(selector)
            if result is not None:
                return result
            return await self._query_selector_shadow(selector, base)

        async def _query_selector_all(self, selector: str, base: Optional[NodriverElement] = None):
            context = self._current_context(base)
            if context is not None:
                result = await context.query_selector_all(selector)
            else:
                result = await self._active_tab.query_selector_all(selector)
            if result:
                return result
            return await self._query_selector_all_shadow(selector, base)

        def _find_element(
            self, by: str, value: str, base: Optional[NodriverElement] = None
        ) -> NodriverElement:
            selector = self._selector_from(by, value)
            element = self._run(self._query_selector(selector, base))
            if not element:
                raise NoSuchElementException(
                    f"Element not found using {by} with value {value}"
                )
            return NodriverElement(self, element)

        def _find_elements(
            self, by: str, value: str, base: Optional[NodriverElement] = None
        ) -> List[NodriverElement]:
            selector = self._selector_from(by, value)
            elements = self._run(self._query_selector_all(selector, base)) or []
            return [NodriverElement(self, item) for item in elements]

        async def _query_selector_shadow(
            self, selector: str, base: Optional[NodriverElement] = None
        ):
            matches = await self._query_selector_all_shadow(
                selector, base, first_only=True
            )
            if matches:
                return matches[0]
            return None

        async def _query_selector_all_shadow(
            self,
            selector: str,
            base: Optional[NodriverElement] = None,
            first_only: bool = False,
        ):
            if nodriver_core_element is None or nodriver_util is None:
                return []
            doc = await self._active_tab.send(cdp.dom.get_document(-1, True))
            try:
                search_id, result_count = await self._active_tab.send(
                    cdp.dom.perform_search(
                        selector, include_user_agent_shadow_dom=True
                    )
                )
            except Exception:
                return []
            collected: List[Any] = []
            base_node_id = None
            if base is not None and isinstance(base, NodriverElement):
                base_node_id = getattr(base._element.node, "node_id", None)
            fetched = 0
            try:
                while fetched < result_count:
                    end = min(result_count, fetched + 20)
                    try:
                        node_ids = await self._active_tab.send(
                            cdp.dom.get_search_results(search_id, fetched, end)
                        )
                    except Exception:
                        break
                    fetched = end
                    for node_id in node_ids or []:
                        if base_node_id is not None and not self._node_is_descendant(
                            doc, base_node_id, node_id
                        ):
                            continue
                        node = nodriver_util.filter_recurse(
                            doc, lambda item, target=node_id: item.node_id == target
                        )
                        if not node:
                            continue
                        collected.append(
                            nodriver_core_element.create(node, self._active_tab, doc)
                        )
                        if first_only and collected:
                            return collected
                return collected
            finally:
                try:
                    await self._active_tab.send(
                        cdp.dom.discard_search_results(search_id)
                    )
                except Exception:
                    pass

        def _node_is_descendant(
            self, doc: Any, ancestor_id: Any, candidate_id: Any
        ) -> bool:
            if nodriver_util is None:
                return False
            ancestor = nodriver_util.filter_recurse(
                doc, lambda item, target=ancestor_id: item.node_id == target
            )
            if not ancestor:
                return False
            if ancestor.node_id == candidate_id:
                return True
            descendant = nodriver_util.filter_recurse(
                ancestor, lambda item, target=candidate_id: item.node_id == target
            )
            return descendant is not None

        def _format_keys(self, value: Any) -> str:
            if isinstance(value, str):
                return value
            if value == Keys.ENTER:
                return "\r"
            if value == Keys.END:
                return "\uE010"
            if isinstance(value, (list, tuple)):
                return "".join(self._format_keys(v) for v in value)
            return str(value)

        def _press_and_hold(self, element: NodriverElement, seconds: float) -> None:
            self._run(self._press_and_hold_async(element, seconds))

        async def _press_and_hold_async(
            self, element: NodriverElement, seconds: float
        ) -> None:
            await element._element.scroll_into_view()
            coords = await element._element.apply(
                "(elem) => {"
                "  const rect = elem.getBoundingClientRect();"
                "  return {"
                "    x: rect.left + (rect.width / 2),"
                "    y: rect.top + (rect.height / 2)"
                "  };"
                "}"
            )
            if not isinstance(coords, dict):
                raise RuntimeError("Unable to resolve element coordinates")
            x = float(coords.get("x", 0))
            y = float(coords.get("y", 0))
            await self._active_tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseMoved",
                    x=x,
                    y=y,
                    button=cdp.input_.MouseButton.NONE,
                    buttons=0,
                )
            )
            await self._active_tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mousePressed",
                    x=x,
                    y=y,
                    button=cdp.input_.MouseButton.LEFT,
                    buttons=1,
                )
            )
            try:
                await asyncio.sleep(max(seconds, 0.2))
            finally:
                await self._active_tab.send(
                    cdp.input_.dispatch_mouse_event(
                        type_="mouseReleased",
                        x=x,
                        y=y,
                        button=cdp.input_.MouseButton.LEFT,
                        buttons=0,
                    )
                )

        # ------------------------------------------------------------------
        # WebDriver compatible API
        # ------------------------------------------------------------------
        def get(self, url: str) -> None:
            self._run(self._active_tab.get(url))
            self._refresh_handles()

        def find_element(self, by: str, value: str) -> NodriverElement:
            return self._find_element(by, value)

        def find_elements(self, by: str, value: str) -> List[NodriverElement]:
            return self._find_elements(by, value)

        def execute_script(self, script: str, *args: Any) -> Any:
            if args and isinstance(args[0], NodriverElement):
                target = args[0]
                body = script.replace("arguments[0]", "elem")
                body = body.strip()
                if not (body.startswith("return") or body.startswith("(") or body.startswith("elem") or body.startswith("{")):
                    body = f"{{ {body} }}"
                return self._run(
                    target._element.apply(f"(elem) => {body}")
                )
            return self._run(self._active_tab.evaluate(script, return_by_value=True))

        @property
        def window_handles(self) -> List[str]:
            self._refresh_handles()
            return list(self._handles)

        @property
        def current_window_handle(self) -> Optional[str]:
            if self._active_tab and self._active_tab.target:
                return self._active_tab.target.target_id
            return None

        @property
        def current_url(self) -> str:
            if self._active_tab and self._active_tab.target:
                return self._active_tab.target.url or ""
            return ""

        def close(self) -> None:
            if self._active_tab:
                self._run(self._active_tab.close())
            self._refresh_handles()
            if self._handles:
                self._switch_window(self._handles[0])

        def quit(self) -> None:
            try:
                if self._browser:
                    self._browser.stop()
            finally:
                if self._loop.is_running():
                    self._loop.call_soon_threadsafe(self._loop.stop)
                self._loop_thread.join(timeout=1)

        def set_script_timeout(self, timeout: Any) -> None:
            self._script_timeout = timeout

        def get_log(self, *_args: Any, **_kwargs: Any) -> List[Any]:
            return []


else:

    NodriverElement = None
    NodriverAlert = None
    NodriverSwitchTo = None
    NodriverSelect = None
    NodriverWebDriver = None


if ChromiumPage is not None:

    class DrissionElement:
        def __init__(self, driver: "DrissionWebDriver", element: "_ChromiumElement"):
            self._driver = driver
            self._element = element

        def __bool__(self) -> bool:
            return self._element is not None

        def click(self) -> None:
            self._element.click()

        def clear(self) -> None:
            try:
                self._element.clear()
            except Exception:
                self._driver.execute_script(
                    "arguments[0].value = '';"
                    "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                    "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                    self,
                )

        def find_element(self, by: str, value: str) -> "DrissionElement":
            return self._driver._find_element(by, value, base=self)

        def find_elements(self, by: str, value: str) -> List["DrissionElement"]:
            return self._driver._find_elements(by, value, base=self)

        def get_attribute(self, name: str) -> Optional[str]:
            try:
                value = self._element.attr(name)
            except Exception:
                value = None
            if value is not None:
                return str(value)
            script = (
                "return (function(elem, prop) {"
                "  if (!elem) { return null; }"
                "  const attr = elem.getAttribute(prop);"
                "  if (attr !== null) { return attr; }"
                "  const val = elem[prop];"
                "  if (val === undefined || val === null) { return null; }"
                "  return String(val);"
                "})(arguments[0], arguments[1]);"
            )
            result = self._driver.execute_script(script, self, name)
            if result is None:
                return None
            return str(result)

        def is_selected(self) -> bool:
            script = (
                "return (function(elem) {"
                "  if (!elem) { return false; }"
                "  return Boolean(elem.checked ?? elem.selected ?? false);"
                "})(arguments[0]);"
            )
            return bool(self._driver.execute_script(script, self))

        def is_displayed(self) -> bool:
            script = """
                return (function(elem) {
                  if (!elem || !(elem instanceof Element)) {
                    return false;
                  }
                  if (elem.hasAttribute && elem.hasAttribute('hidden')) {
                    return false;
                  }
                  const style = window.getComputedStyle(elem);
                  if (!style) {
                    return false;
                  }
                  if (style.display === 'none' || style.visibility === 'hidden' || style.visibility === 'collapse') {
                    return false;
                  }
                  if (style.pointerEvents === 'none') {
                    return false;
                  }
                  const rect = elem.getBoundingClientRect();
                  const hasSize = rect && (rect.width !== 0 || rect.height !== 0);
                  if (!hasSize && elem.getClientRects().length === 0) {
                    return false;
                  }
                  const ariaHidden = elem.getAttribute && elem.getAttribute('aria-hidden');
                  if (ariaHidden && ariaHidden.toLowerCase() === 'true') {
                    return false;
                  }
                  let current = elem;
                  while (current) {
                    if (current.hasAttribute && current.hasAttribute('hidden')) {
                      return false;
                    }
                    const root = current.getRootNode && current.getRootNode();
                    current = current.parentElement || (root && root.host) || null;
                  }
                  return true;
                })(arguments[0]);
            """
            return bool(self._driver.execute_script(script, self))

        def is_enabled(self) -> bool:
            script = """
                return (function(elem) {
                  if (!elem) { return false; }
                  if (elem.disabled) { return false; }
                  if (elem.hasAttribute && elem.hasAttribute('disabled')) { return false; }
                  const ariaDisabled = elem.getAttribute && elem.getAttribute('aria-disabled');
                  if (ariaDisabled && ariaDisabled.toLowerCase() === 'true') { return false; }
                  const fieldset = elem.closest ? elem.closest('fieldset') : null;
                  if (fieldset && fieldset.disabled) { return false; }
                  const style = window.getComputedStyle(elem);
                  if (style && style.pointerEvents === 'none') { return false; }
                  return true;
                })(arguments[0]);
            """
            return bool(self._driver.execute_script(script, self))

        @property
        def text(self) -> str:
            try:
                value = self._element.text
            except Exception:
                value = ""
            return value or ""

        def send_keys(self, value: Any) -> None:
            text = self._driver._format_keys(value)
            if not text:
                return
            try:
                self._element.input(text, clear=False)
            except Exception:
                self._driver.execute_script(
                    "(function(elem, val) {"
                    "  if (!elem) { return; }"
                    "  if ('value' in elem) { elem.value += val; }"
                    "  else { elem.innerText += val; }"
                    "  elem.dispatchEvent(new Event('input', {bubbles: true}));"
                    "  elem.dispatchEvent(new Event('change', {bubbles: true}));"
                    "})(arguments[0], arguments[1]);",
                    self,
                    text,
                )


    class DrissionAlert:
        def __init__(self, driver: "DrissionWebDriver"):
            self._driver = driver

        def accept(self) -> None:
            self._driver._page.handle_alert(accept=True)

        def dismiss(self) -> None:
            self._driver._page.handle_alert(accept=False)


    class DrissionSwitchTo:
        def __init__(self, driver: "DrissionWebDriver"):
            self._driver = driver

        def window(self, handle: str) -> None:
            self._driver._switch_window(handle)

        def frame(self, frame_reference: DrissionElement) -> None:
            if not isinstance(frame_reference, DrissionElement):
                raise TypeError("frame reference must be a DrissionElement")
            frame = frame_reference._element.get_frame()
            if frame is None:
                raise NoSuchElementException("Unable to switch to frame")
            self._driver._frame_stack.append(frame)

        def default_content(self) -> None:
            self._driver._frame_stack.clear()

        @property
        def alert(self) -> DrissionAlert:
            return DrissionAlert(self._driver)


    class DrissionSelect:
        def __init__(self, element: DrissionElement):
            if element._element.tag != "select":
                raise ValueError("DrissionSelect only supports <select> elements")
            self._element = element

        def _dispatch_change(self) -> None:
            self._element._driver.execute_script(
                "(function(elem) {"
                "  if (!elem) { return; }"
                "  elem.dispatchEvent(new Event('input', {bubbles: true}));"
                "  elem.dispatchEvent(new Event('change', {bubbles: true}));"
                "})(arguments[0]);",
                self._element,
            )

        def select_by_value(self, value: str) -> None:
            script = (
                "return (function(elem, target) {"
                "  if (!elem || !elem.options) { return false; }"
                "  const options = Array.from(elem.options);"
                "  const match = options.find(opt => opt.value === target);"
                "  if (!match) { return false; }"
                "  elem.value = match.value;"
                "  return true;"
                "})(arguments[0], arguments[1]);"
            )
            success = self._element._driver.execute_script(
                script, self._element, value
            )
            if not success:
                raise NoSuchElementException(
                    f"Cannot locate option with value: {value}"
                )
            self._dispatch_change()

        def select_by_visible_text(self, text: str) -> None:
            script = (
                "return (function(elem, label) {"
                "  if (!elem || !elem.options) { return false; }"
                "  const options = Array.from(elem.options);"
                "  const match = options.find(opt => (opt.textContent || '').trim() === label.trim());"
                "  if (!match) { return false; }"
                "  elem.value = match.value;"
                "  return true;"
                "})(arguments[0], arguments[1]);"
            )
            success = self._element._driver.execute_script(
                script, self._element, text
            )
            if not success:
                raise NoSuchElementException(
                    f"Cannot locate option with text: {text}"
                )
            self._dispatch_change()


    class DrissionWebDriver:
        def __init__(self, config_dict: dict):
            if ChromiumPage is None or ChromiumOptions is None:
                raise RuntimeError("DrissionPage is not installed")

            self._config = config_dict
            self._options = self._build_options(config_dict)
            try:
                self._page = ChromiumPage(addr_or_opts=self._options)
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Unable to launch Chromium browser for DrissionPage. "
                    "Please install Chrome or specify its path in the settings."
                ) from exc
            self._frame_stack: List["_ChromiumFrame"] = []
            self.switch_to = DrissionSwitchTo(self)
            self._script_timeout = None

            self._page.add_init_js(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )

        # ------------------------------------------------------------------
        # helpers
        # ------------------------------------------------------------------
        def _build_options(self, config_dict: dict) -> ChromiumOptions:
            opts = ChromiumOptions()
            headless = bool(config_dict.get("advanced", {}).get("headless", False))
            opts.headless(headless)
            opts.set_argument("--disable-features=TranslateUI")
            opts.set_argument("--disable-translate")
            opts.set_argument("--disable-web-security")
            opts.set_argument("--no-sandbox")
            opts.set_argument("--disable-blink-features=AutomationControlled")
            opts.set_argument("--password-store=basic")
            lang = config_dict.get("language", "zh-TW")
            opts.set_argument(f"--lang={lang}")
            if not headless:
                opts.set_argument("--start-maximized")
            browser = config_dict.get("browser", "chrome")
            if browser == "brave":
                brave_path = get_brave_bin_path()
                if brave_path and os.path.exists(brave_path):
                    opts.set_browser_path(brave_path)
            elif browser == "chrome":
                chrome_path = config_dict.get("chrome_path")
                if chrome_path and os.path.exists(chrome_path):
                    opts.set_browser_path(chrome_path)
            opts.set_pref("credentials_enable_service", False)
            opts.set_pref("profile.password_manager_enabled", False)
            opts.set_load_mode("eager")
            return opts

        def _current_context(self):
            if self._frame_stack:
                return self._frame_stack[-1]
            return self._page

        def _switch_window(self, handle: str) -> None:
            if handle not in self.window_handles:
                raise NoSuchWindowException(f"No window with handle {handle}")
            self._page.activate_tab(handle)
            self._frame_stack.clear()

        def _translate_locator(self, by: str, value: str):
            if by == By.CSS_SELECTOR:
                return value
            if by == By.ID:
                return f"#{value}"
            if by == By.NAME:
                escaped = value.replace("'", "\\'")
                return f"[name='{escaped}']"
            if by == By.CLASS_NAME:
                classes = ".".join(part for part in value.split() if part)
                return f".{classes}" if classes else value
            if by == By.TAG_NAME:
                return value
            if by == By.XPATH:
                return ("xpath", value)
            raise NotImplementedError(
                f"By strategy {by} is not supported in drissionpage mode"
            )

        def _find_element(
            self, by: str, value: str, base: Optional[DrissionElement] = None
        ) -> DrissionElement:
            locator = self._translate_locator(by, value)
            timeout = None
            if isinstance(locator, tuple):
                query, selector = locator
            else:
                query, selector = None, locator
            context = base._element if base is not None else self._current_context()
            result = None
            try:
                if query:
                    result = context.ele((query, selector), timeout=timeout)
                else:
                    result = context.ele(selector, timeout=timeout)
            except Exception:
                result = None
            if result is None:
                raise NoSuchElementException(
                    f"No element found using locator ({by}, {value})"
                )
            return DrissionElement(self, result)

        def _find_elements(
            self, by: str, value: str, base: Optional[DrissionElement] = None
        ) -> List[DrissionElement]:
            locator = self._translate_locator(by, value)
            context = base._element if base is not None else self._current_context()
            if isinstance(locator, tuple):
                query, selector = locator
            else:
                query, selector = None, locator
            try:
                if query:
                    results = context.eles((query, selector), timeout=0)
                else:
                    results = context.eles(selector, timeout=0)
            except Exception:
                results = []
            return [DrissionElement(self, item) for item in results or []]

        def _unwrap_argument(self, value: Any) -> Any:
            if isinstance(value, DrissionElement):
                return value._element
            return value

        def _format_keys(self, value: Any) -> str:
            if isinstance(value, str):
                return value
            if value == Keys.ENTER:
                return "\r"
            if value == Keys.END:
                return "\uE010"
            if isinstance(value, (list, tuple)):
                return "".join(self._format_keys(v) for v in value)
            return str(value)

        def _press_and_hold(self, element: DrissionElement, seconds: float) -> None:
            seconds = max(float(seconds), 0.2)
            try:
                rect = element._element.rect
                x = float(rect.get("x", 0)) + float(rect.get("width", 0)) / 2
                y = float(rect.get("y", 0)) + float(rect.get("height", 0)) / 2
                self._page.run_cdp(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mouseMoved",
                        "x": x,
                        "y": y,
                        "buttons": 0,
                    },
                )
                self._page.run_cdp(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mousePressed",
                        "x": x,
                        "y": y,
                        "button": "left",
                        "clickCount": 1,
                    },
                )
                time.sleep(seconds)
                self._page.run_cdp(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mouseReleased",
                        "x": x,
                        "y": y,
                        "button": "left",
                        "clickCount": 1,
                    },
                )
            except Exception:
                element.click()
                time.sleep(seconds)

        # ------------------------------------------------------------------
        # webdriver-like interface
        # ------------------------------------------------------------------
        def get(self, url: str) -> None:
            self._page.get(url)

        def find_element(self, by: str, value: str) -> DrissionElement:
            return self._find_element(by, value)

        def find_elements(self, by: str, value: str) -> List[DrissionElement]:
            return self._find_elements(by, value)

        def execute_script(self, script: str, *args: Any) -> Any:
            prepared_args = [self._unwrap_argument(arg) for arg in args]
            wrapped = (
                "return (function() {"
                f"{script}"
                "}).apply(null, arguments);"
            )
            context = self._current_context()
            return context.run_js(wrapped, *prepared_args)

        def close(self) -> None:
            self._page.close()
            self._frame_stack.clear()

        def quit(self) -> None:
            try:
                self._page.quit()
            finally:
                self._frame_stack.clear()

        def set_script_timeout(self, timeout: Any) -> None:
            self._script_timeout = timeout

        def get_log(self, *_args: Any, **_kwargs: Any) -> List[Any]:
            return []

        @property
        def current_url(self) -> str:
            try:
                return self._current_context().url
            except Exception:
                return ""

        @property
        def current_window_handle(self) -> Optional[str]:
            try:
                return self._page.tab_id
            except Exception:
                return None

        @property
        def window_handles(self) -> List[str]:
            try:
                handles = list(self._page.tab_ids)
            except Exception:
                handles = []
            return handles

        @property
        def switch_to_alert(self) -> DrissionAlert:
            return DrissionAlert(self)

else:

    DrissionElement = None
    DrissionAlert = None
    DrissionSwitchTo = None
    DrissionSelect = None
    DrissionWebDriver = None


def Select(element):
    if NodriverElement is not None and isinstance(element, NodriverElement):
        return NodriverSelect(element)
    if DrissionElement is not None and isinstance(element, DrissionElement):
        return DrissionSelect(element)
    if SeleniumSelect is None:
        raise RuntimeError("Selenium Select is unavailable")
    return SeleniumSelect(element)


def t_or_f(arg):
    ret = False
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
        ret = True
    elif 'YES'.startswith(ua):
        ret = True
    return ret

def sx(s1):
    key=18
    return ''.join(chr(ord(a) ^ key) for a in s1)

def decryptMe(b):
    s=""
    if(len(b)>0):
        s=sx(base64.b64decode(b).decode("UTF-8"))
    return s

def encryptMe(s):
    data=""
    if(len(s)>0):
        data=base64.b64encode(sx(s).encode('UTF-8')).decode("UTF-8")
    return data


def _perform_press_and_hold(driver, element, hold_seconds: float) -> None:
    hold_seconds = max(float(hold_seconds), 0.2)
    if NodriverElement is not None and isinstance(element, NodriverElement):
        driver._press_and_hold(element, hold_seconds)
        return
    if DrissionElement is not None and isinstance(element, DrissionElement):
        driver._press_and_hold(element, hold_seconds)
        return

    actions = ActionChains(driver)
    actions.click_and_hold(element).pause(hold_seconds).release().perform()


def solve_press_and_hold_if_needed(driver, hold_seconds: float = 5.0) -> bool:
    if driver is None:
        return False

    marker_script = """
        (() => {
          const markers = [
            '按住不放',
            '按著不放',
            '按住確認',
            '按住以確認',
            'Press and hold',
            'Hold to verify'
          ];
          const candidates = Array.from(document.querySelectorAll('button, [role="button"]'));
          for (const el of document.querySelectorAll('[data-maxbot-press-hold]')) {
            el.removeAttribute('data-maxbot-press-hold');
          }
          for (const el of candidates) {
            const label = (el.innerText || el.textContent || '').trim();
            if (!label) {
              continue;
            }
            if (markers.some((word) => label.includes(word))) {
              el.setAttribute('data-maxbot-press-hold', 'true');
              return true;
            }
          }
          return false;
        })()
    """

    cleanup_script = """
        for (const el of document.querySelectorAll('[data-maxbot-press-hold]')) {
          el.removeAttribute('data-maxbot-press-hold');
        }
    """

    def _candidate_frames():
        try:
            frames = driver.find_elements(By.CSS_SELECTOR, "iframe")
        except Exception:
            return []
        keywords = (
            "captcha",
            "verify",
            "verification",
            "px-captcha",
            "人類驗證",
            "驗證挑戰",
        )
        filtered = []
        for frame in frames:
            try:
                title = (frame.get_attribute("title") or "").lower()
                src = (frame.get_attribute("src") or "").lower()
            except Exception:
                title = src = ""
            text = f"{title} {src}"
            if any(keyword in text for keyword in keywords):
                filtered.append(frame)
        return filtered or frames

    contexts: List[Optional[Any]] = [None]
    contexts.extend(_candidate_frames())

    for frame in contexts:
        element = None
        try:
            if frame is not None:
                driver.switch_to.frame(frame)
            try:
                found = driver.execute_script(marker_script)
            except Exception:
                continue

            if not found:
                continue

            try:
                element = driver.find_element(
                    By.CSS_SELECTOR, "[data-maxbot-press-hold='true']"
                )
            except NoSuchElementException:
                element = None

            if element is None:
                try:
                    driver.execute_script(cleanup_script)
                except Exception:
                    pass
                continue

            durations = [
                max(hold_seconds, 0.8),
                max(hold_seconds + 2.0, 3.0),
                max(hold_seconds + 4.0, 6.0),
            ]

            success = False
            for duration in durations:
                try:
                    _perform_press_and_hold(driver, element, duration)
                except Exception:
                    break
                time.sleep(0.6)
                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR, "[data-maxbot-press-hold='true']"
                    )
                except NoSuchElementException:
                    success = True
                    break
                except Exception:
                    break
            try:
                driver.execute_script(cleanup_script)
            except Exception:
                pass

            if success:
                return True
        finally:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

    return False


def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict(args):
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    # allow assign config by command line.
    if not args.input is None:
        if len(args.input) > 0:
            config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict

def write_last_url_to_file(url):
    outfile = None
    if platform.system() == 'Windows':
        outfile = open(CONST_MAXBOT_LAST_URL_FILE, 'w', encoding='UTF-8')
    else:
        outfile = open(CONST_MAXBOT_LAST_URL_FILE, 'w')

    if not outfile is None:
        outfile.write("%s" % url)

def read_last_url_from_file():
    ret = ""
    with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
        ret = text_file.readline()
    return ret


def get_favoriate_extension_path(webdriver_path):
    print("webdriver_path:", webdriver_path)
    extension_list = []
    extension_list.append(os.path.join(webdriver_path,"Adblock_3.18.1.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"Buster_2.0.1.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"proxy-switchyomega_2.5.21.0.crx"))
    return extension_list

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_brave_bin_path():
    brave_path = ""
    if platform.system() == 'Windows':
        brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = os.path.expanduser('~') + "\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = "D:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

    if platform.system() == 'Linux':
        brave_path = "/usr/bin/brave-browser"

    if platform.system() == 'Darwin':
        brave_path = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'

    return brave_path

def get_chrome_options(webdriver_path, adblock_plus_enable, browser="chrome", headless = False):
    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
        extension_list = get_favoriate_extension_path(webdriver_path)
        for ext in extension_list:
            if os.path.exists(ext):
                chrome_options.add_extension(ext)
    if headless:
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--no-sandbox");

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if browser=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            chrome_options.binary_location = brave_path

    chrome_options.page_load_strategy = 'eager'
    #chrome_options.page_load_strategy = 'none'
    chrome_options.unhandled_prompt_behavior = "accept"

    return chrome_options

def load_chromdriver_normal(config_dict, driver_type):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    driver = None

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("WebDriver not exist, try to download to:", webdriver_path)
        install_chromedriver_binary(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(URL_CHROME_DRIVER)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser=config_dict["browser"], headless=config_dict["advanced"]["headless"])
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            if show_debug_message:
                print(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

                # remove exist chromedriver, download again.
                try:
                    print("Deleting exist and download ChromeDriver again.")
                    os.unlink(chromedriver_path)
                except Exception as exc2:
                    print(exc2)
                    pass

                install_chromedriver_binary(webdriver_path)
                chrome_service = Service(chromedriver_path)
                try:
                    chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser=config_dict["browser"], headless=config_dict["advanced"]["headless"])
                    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                except Exception as exc2:
                    print("Selenium 4.11.0 Release with Chrome For Testing Browser.")
                    try:
                        chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser=config_dict["browser"], headless=config_dict["advanced"]["headless"])
                        driver = webdriver.Chrome(service=Service(), options=chrome_options)
                    except Exception as exc3:
                        print(exc3)
                        pass


    if driver_type=="stealth":
        from selenium_stealth import stealth
        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )
    #print("driver capabilities", driver.capabilities)

    return driver

def clean_uc_exe_cache():
    exe_name = "chromedriver%s"

    platform = sys.platform
    if platform.endswith("win32"):
        exe_name %= ".exe"
    if platform.endswith(("linux", "linux2")):
        exe_name %= ""
    if platform.endswith("darwin"):
        exe_name %= ""

    d = ""
    if platform.endswith("win32"):
        d = "~/appdata/roaming/undetected_chromedriver"
    elif "LAMBDA_TASK_ROOT" in os.environ:
        d = "/tmp/undetected_chromedriver"
    elif platform.startswith(("linux", "linux2")):
        d = "~/.local/share/undetected_chromedriver"
    elif platform.endswith("darwin"):
        d = "~/Library/Application Support/undetected_chromedriver"
    else:
        d = "~/.undetected_chromedriver"
    data_path = os.path.abspath(os.path.expanduser(d))

    is_cache_exist = False
    p = pathlib.Path(data_path)
    files = list(p.rglob("*chromedriver*?"))
    for file in files:
        if os.path.exists(str(file)):
            is_cache_exist = True
            try:
                os.unlink(str(file))
            except Exception as exc2:
                print(exc2)
                pass

    return is_cache_exist

def get_uc_options(uc, config_dict, webdriver_path):
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    #options.page_load_strategy = 'none'
    options.unhandled_prompt_behavior = "accept"

    #print("strategy", options.page_load_strategy)

    if config_dict["advanced"]["adblock_plus_enable"]:
        load_extension_path = ""
        extension_list = get_favoriate_extension_path(webdriver_path)
        for ext in extension_list:
            ext = ext.replace('.crx','')
            if os.path.exists(ext):
                load_extension_path += ("," + os.path.abspath(ext))
        if len(load_extension_path) > 0:
            print('load-extension:', load_extension_path[1:])
            options.add_argument('--load-extension=' + load_extension_path[1:])

    if config_dict["advanced"]["headless"]:
        #options.add_argument('--headless')
        options.add_argument('--headless=new')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')
    options.add_argument('--disable-web-security')
    options.add_argument("--no-sandbox");

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if config_dict["browser"]=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            options.binary_location = brave_path

    return options

def load_chromdriver_uc(config_dict):
    import undetected_chromedriver as uc

    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not exist, try to download to:", webdriver_path)
        install_chromedriver_binary(webdriver_path)
    else:
        print("ChromeDriver exist:", chromedriver_path)


    driver = None
    if os.path.exists(chromedriver_path):
        # use chromedriver_autodownload instead of uc auto download.
        is_cache_exist = clean_uc_exe_cache()

        try:
            options = get_uc_options(uc, config_dict, webdriver_path)
            driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

            # remove exist chromedriver, download again.
            try:
                print("Deleting exist and download ChromeDriver again.")
                os.unlink(chromedriver_path)
            except Exception as exc2:
                print(exc2)
                pass

            install_chromedriver_binary(webdriver_path)
            try:
                options = get_uc_options(uc, config_dict, webdriver_path)
                driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
            except Exception as exc2:
                print(exc2)
                pass
    else:
        print("WebDriver not found at path:", chromedriver_path)

    if driver is None:
        print('WebDriver object is None..., try again..')
        try:
            driver = uc.Chrome(options=options, headless=config_dict["advanced"]["headless"])
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(config_dict, driver_type)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver


def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict):
    global driver

    # read config.
    homepage = config_dict["homepage"]

    if not config_dict is None:
        # output config:
        print("maxbot app version", CONST_APP_VERSION)
        print("python version", platform.python_version())
        print("config", config_dict)

        homepage = config_dict["homepage"]
        adult_picker = config_dict["adult_picker"]
        book_now_time = config_dict["book_now_time"]
        book_now_time_alt = config_dict["book_now_time_alt"]
        
        user_name = config_dict["user_name"]
        user_gender = config_dict["user_gender"]
        user_phone = config_dict["user_phone"]
        user_email = config_dict["user_email"]

        cardholder_name = config_dict["cardholder_name"]
        cardholder_email = config_dict["cardholder_email"]
        cc_number = config_dict["cc_number"]
        cc_exp = config_dict["cc_exp"]
        cc_ccv = config_dict["cc_ccv"]

        if 'cc_auto_submit' in config_dict:
            cc_auto_submit = config_dict["cc_auto_submit"]

    # entry point
    if homepage is None:
        homepage = ""
    if len(homepage) == 0:
        homepage = CONST_HOMEPAGE_DEFAULT

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    if config_dict["browser"] in ["chrome","brave"]:
        driver_type = config_dict.get("webdriver_type", CONST_WEBDRIVER_TYPE_SELENIUM)
        if driver_type == CONST_WEBDRIVER_TYPE_NODRIVER:
            driver = load_nodriver(config_dict)
        elif driver_type == CONST_WEBDRIVER_TYPE_DRISSION:
            driver = load_drissionpage(config_dict)
        elif driver_type == CONST_WEBDRIVER_TYPE_UC:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(config_dict)
        else:
            # method 6: Selenium Stealth
            driver = load_chromdriver_normal(config_dict, driver_type)

    if config_dict["browser"] == "firefox":
        # default os is linux/mac
        # download url: https://github.com/mozilla/geckodriver/releases
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")

        webdriver_service = Service(chromedriver_path)
        driver = None
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if config_dict["advanced"]["headless"]:
                options.add_argument('--headless')
                #options.add_argument('--headless=new')
            if platform.system().lower()=="windows":
                binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = os.path.expanduser('~') + "\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"
                options.binary_location = binary_path

            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)
            else:
                print(exc)

    if config_dict["browser"] == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser="edge", headless=config_dict["advanced"]["headless"])

        driver = None
        try:
            driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if config_dict["browser"] == "safari":
        driver = None
        try:
            driver = webdriver.Safari()
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            print("goto url:", homepage)
            driver.get(homepage)
            time.sleep(3.0)
        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exce1)
            pass

    return driver


def load_nodriver(config_dict):
    if NodriverWebDriver is None:
        raise RuntimeError("nodriver is required but is not available")
    return NodriverWebDriver(config_dict)


def load_drissionpage(config_dict):
    if DrissionWebDriver is None:
        raise RuntimeError("DrissionPage is required but is not available")
    return DrissionWebDriver(config_dict)

def is_House_Rules_poped(driver):
    ret = False
    #---------------------------
    # part 1: check house rule pop
    #---------------------------
    house_rules_div = None
    try:
        house_rules_div = driver.find_element(By.ID, 'house-rules')
    except Exception as exc:
        pass

    houses_rules_button = None
    if house_rules_div is not None:
        is_visible = False
        try:
            if house_rules_div.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                #houses_rules_button = house_rules_div.find_element(By.TAG_NAME, 'button')
                houses_rules_button = house_rules_div.find_element(By.XPATH, '//button[@data-cy="confirm-house-rule"]')
            except Exception as exc:
                pass

    if houses_rules_button is not None:
        #print("found disabled houses_rules_button, enable it.")
        
        # method 1: force enable, fail.
        # driver.execute_script("arguments[0].disabled = false;", commit)

        # metho 2: scroll to end.
        houses_rules_scroll = None
        try:
            houses_rules_scroll = house_rules_div.find_element(By.XPATH, '//div[@data-show-scrollbar="true"]/div/div')
        except Exception as exc:
            pass
        
        if houses_rules_scroll is not None:
            try:
                if houses_rules_scroll.is_enabled():
                    #print("found enabled scroll bar. scroll to end.")
                    houses_rules_scroll.click()
                    
                    #PLAN A -- fail.
                    #print('send end key.')
                    #houses_rules_scroll.send_keys(Keys.END)
                    
                    #PLAN B -- OK.
                    #driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", houses_rules_scroll)
                    driver.execute_script("arguments[0].innerHTML='';", houses_rules_scroll);
            except Exception as exc:
                #print("check house rules fail...")
                #print(exc)
                pass


        houses_rules_is_visible = False
        try:
            if houses_rules_button.is_enabled():
                houses_rules_is_visible = True
        except Exception as exc:
            pass
        
        if houses_rules_is_visible:
            print("found enabled houses_rules_button.")
            try:
                houses_rules_button.click()
            except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", houses_rules_button);
                    except Exception as exc2:
                        pass


    return ret

def button_submit(el_form, by_method, query_keyword):
    # user name
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        is_visible = False
        try:
            if el_text_name.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        
        if is_visible:
            try:
                el_text_name.click()
            except Exception as exc:
                print("send el_text_%s fail" % (query_keyword))
                #print(exc)

                try:
                    driver.execute_script("arguments[0].click();", el_text_name);
                except Exception as exc:
                    print("try javascript click on el_text_%s, still fail." % (query_keyword))
                    #print(exc)


def click_radio(el_form, by_method, query_keyword, assign_method='CLICK'):
    is_radio_selected = False
    # user name
    
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))

    if el_text_name is not None:
        #print("found el_text_name")
        try:
            is_radio_selected = el_text_name.is_selected()
        except Exception as exc:
            pass

        if not is_radio_selected:
            if assign_method=='CLICK':
                try:
                    el_text_name.click()
                except Exception as exc:
                    print("send el_text_%s fail" % (query_keyword))

                    #print(exc)
                    try:
                        driver.execute_script("arguments[0].click();", el_text_name);
                    except Exception as exc:
                        print("try javascript click on el_text_%s, still fail." % (query_keyword))
                        #print(exc)

            if assign_method=='JS':
                try:
                    driver.execute_script("arguments[0].checked;", el_text_name);
                except Exception as exc:
                    print("send el_text_%s fail" % (query_keyword))
                    print(exc)
        else:
            pass
            #print("text not empty, value:", text_name_value)

    return is_radio_selected


def checkbox_agree(el_form, by_method, query_keyword, assign_method='CLICK'):
    ret = False
    # user name
    
    el_text_name = None
    el_label_name = None

    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
        if by_method == By.ID:
            el_label_name = el_form.find_element(By.XPATH, '//label[@for="%s"]' % (query_keyword))
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        ret = el_text_name.is_selected()
        if not el_text_name.is_selected():
            if assign_method=='CLICK':
                #el_text_name.click()
                if el_label_name is not None:
                    print('click label for chekbox:', query_keyword)
                    try:
                        el_label_name.click()
                    except Exception as exc:
                        print("send el_text_%s fail" % (query_keyword))
                        #print(exc)
                        try:
                            driver.execute_script("arguments[0].click();", el_label_name);
                        except Exception as exc:
                            print("try javascript click on el_text_%s, still fail." % (query_keyword))
                            #print(exc)

            if assign_method=='JS':
                driver.execute_script("arguments[0].checked;", el_text_name);
        else:
            pass
            #print("text not empty, value:", text_name_value)

    return ret

# assign value in text.
# return:
#   True: value in text
#   False: assign fail.
def fill_text_by_default(el_form, by_method, query_keyword, default_value, assign_method='SENDKEY'):
    ret = False

    # user name
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        text_name_value = None
        try:
            text_name_value = str(el_text_name.get_attribute('value'))
        except Exception as exc:
            pass
        if not text_name_value is None:
            if text_name_value == "":
                #print("try to send keys:", user_name)
                if assign_method=='SENDKEY':
                    try:
                        el_text_name.send_keys(default_value)
                        ret = True
                    except Exception as exc:
                        try:
                            driver.execute_script("arguments[0].value='%s';" % (default_value), el_text_name);
                        except Exception as exc:
                            pass
                if assign_method=='JS':
                    try:
                        driver.execute_script("arguments[0].value='%s';" % (default_value), el_text_name);
                    except Exception as exc:
                        pass

            else:
                ret = True

    return ret

def fill_personal_info(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False
    #print("fill form")

    # user form
    el_form = None
    try:
        el_form = driver.find_element(By.ID, 'contact-form')
    except Exception as exc:
        pass

    if not el_form is None:
        #print("found form")

        # gender-female
        # gender-male
        user_gender = config_dict["user_gender"]
        if user_gender == "先生":
            ret = click_radio(el_form, By.ID, 'gender-male')
        if user_gender == "小姐":
            ret = click_radio(el_form, By.ID, 'gender-female')

        ret = fill_text_by_default(el_form, By.ID, 'name', config_dict["user_name"])
        ret = fill_text_by_default(el_form, By.ID, 'phone', config_dict["user_phone"])
        ret = fill_text_by_default(el_form, By.ID, 'email', config_dict["user_email"])
        
        if(len(config_dict["booking_occasion"]) > 0):
            my_css_selector = 'div[value="'+ config_dict["booking_occasion"] +'"][aria-checked="false"]'
            is_occasion_clicked = force_press_button(driver, By.CSS_SELECTOR, my_css_selector)

        ret = fill_text_by_default(el_form, By.CSS_SELECTOR, 'textarea', config_dict["booking_note"])
        
        cardholder_name = config_dict["cardholder_name"]
        cardholder_email = config_dict["cardholder_email"]
        ret = fill_text_by_default(el_form, By.ID, 'cardholder-name', cardholder_name)
        ret = fill_text_by_default(el_form, By.ID, 'cardholder-email', cardholder_email)

        iframes = None
        try:
            iframes = el_form.find_elements(By.TAG_NAME, "iframe")
        except Exception as exc:
            pass

        if iframes is None:
            iframes = []

        #print('start to travel iframes...')
        cc_check=[False,False,False]
        idx_iframe=0
        for iframe in iframes:
            iframe_url = ""
            try:
                iframe_url = str(iframe.get_attribute('src'))
                #print("url:", iframe_url)
            except Exception as exc:
                print("get iframe url fail.")
                #print(exc)
                pass

            idx_iframe += 1
            try:
                driver.switch_to.frame(iframe)
            except Exception as exc:
                pass

            if "card-number" in iframe_url:
                if not cc_check[0]:
                    #print('check cc-number at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-number', config_dict["cc_number"])
                    cc_check[0]=ret
                    #print("cc-number ret:", ret)
            if "expiration-date" in iframe_url:
                if not cc_check[1]:
                    #print('check cc-exp at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-exp', config_dict["cc_exp"])
                    cc_check[1]=ret
                    #print("cc-exp ret:", ret)
            if "ccv" in iframe_url:
                if not cc_check[2]:
                    #print('check cc-ccv at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-ccv', config_dict["cc_ccv"])
                    cc_check[2]=ret
                    #print("cc-ccv ret:", ret)
            try:
                driver.switch_to.default_content()
            except Exception as exc:
                pass

        pass_all_check = True

        # check credit card.
        for item in cc_check:
            if item == False:
                pass_all_check = False

        # check agree
        try:
            #print("check agree...")
            #driver.execute_script("$(\"input[type='checkbox']\").prop('checked', true);")
            #driver.execute_script("document.getElementById(\"deposit-policy\").checked;")
            #driver.execute_script("document.getElementById(\"privacy-policy\").checked;")
            agree_ret = checkbox_agree(el_form, By.ID, 'deposit-policy')
            if not agree_ret:
                pass_all_check = False
            agree_ret = checkbox_agree(el_form, By.ID, 'privacy-policy')
            if not agree_ret:
                pass_all_check = False
        except Exception as exc:
            print("javascript check agree fail")
            print(exc)
            pass

        #print("auto_submit:", cc_auto_submit)
        if pass_all_check and cc_auto_submit:
            print("press submit button.")
            ret = button_submit(el_form, By.XPATH,'//button[@type="submit"]')
            pass

    return ret

# reutrn: 
#   False: book fail.
#   True: one of book item is seleted, must to do nothing.
# fail_code:
#   0: no target time in button list.
#   1: time_picker not viewable.
#   100: target time full.
#   200: target button is not viewable or not enable.
#   201: target time click fail.
def book_time(el_time_picker_list, target_time):
    ret = False
    fail_code = 0

    is_one_of_time_picket_viewable = False

    for el_time_picker in el_time_picker_list:
        is_visible = False
        try:
            if el_time_picker.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        
        time_picker_text = None
        if is_visible:
            is_one_of_time_picket_viewable = True
            try:
                time_picker_text = str(el_time_picker.text)
            except Exception as exc:
                pass
        
        if time_picker_text is None:
            time_picker_text = ""

        if len(time_picker_text) > 0:
            if ":" in time_picker_text:
                #print("button text:", time_picker_text)
                button_class_string = None
                try:
                    button_class_string = str(el_time_picker.get_attribute('class'))
                except Exception as exc:
                    pass
                if button_class_string is None:
                    button_class_string = ""
                
                is_button_able_to_select = True
                if "selected" in button_class_string:
                    is_button_able_to_select = False
                    ret = True
                    #print("button is selected:", button_class_string, time_picker_text)

                    # no need more loop.
                    break

                if "full" in button_class_string:
                    is_button_able_to_select = False
                    if target_time in time_picker_text:
                        #print("button is full:", button_class_string, time_picker_text)
                        fail_code = 100

                        # no need more loop.
                        break
                
                if is_button_able_to_select:
                    if target_time in time_picker_text:
                        is_able_to_click = True
                        if is_able_to_click:
                            print('click this time block:', time_picker_text)

                            try:
                                el_time_picker.click()
                                ret = True
                            except Exception as exc:
                                # is not clickable at point
                                #print("click target time fail.", exc)
                                fail_code = 201

                                # scroll to view ... fail.
                                #driver.execute_script("console.log(\"scroll to view\");")
                                #driver.execute_script("arguments[0].scrollIntoView(false);", el_time_picker)

                                # JS
                                print('click to button using javascript.')
                                try:
                                    driver.execute_script("console.log(\"click to button.\");")
                                    driver.execute_script("arguments[0].click();", el_time_picker)
                                except Exception as exc:
                                    pass
                        else:
                            fail_code = 200
                            print("target button is not viewable or not enable.")
                            pass

        if not is_one_of_time_picket_viewable:
            fail_code = 1
    return ret, fail_code

def assign_adult_picker(driver, adult_picker, force_adult_picker):
    is_adult_picker_assigned = False

    # member number.
    el_adult_picker = None
    try:
        el_adult_picker = driver.find_element(By.ID, 'adult-picker')
    except Exception as exc:
        pass
    
    if not el_adult_picker is None:
        is_visible = False
        try:
            if el_adult_picker.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            selected_value = None
            try:
                selected_value = str(el_adult_picker.get_attribute('value'))
                #print('seleced value:', selected_value)
            except Exception as exc:
                pass

            if selected_value is None:
                selected_value = ""
            
            if selected_value == "":
                selected_value = "0"

            is_need_assign_select = True
            if selected_value != "0":
                # not is default value, do assign.
                is_need_assign_select = False
                is_adult_picker_assigned = True

                if force_adult_picker:
                    if selected_value != adult_picker:
                        is_need_assign_select = True

            if is_need_assign_select:
                #print('assign new value("%s") for select.' % (adult_picker))
                adult_number_select = Select(el_adult_picker)
                try:
                    adult_number_select.select_by_value(adult_picker)
                    is_adult_picker_assigned = True
                except Exception as exc:
                    print("select_by_value for adult-picker fail")
                    print(exc)
                    pass

    return is_adult_picker_assigned

def assign_time_picker(driver, book_now_time, book_now_time_alt):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    ret = False

    el_time_picker_list = None
    button_query_string = 'button.time-slot'
    try:
        el_time_picker_list = driver.find_elements(By.CSS_SELECTOR, button_query_string)
    except Exception as exc:
        if show_debug_message:
            print("find time buttons excpetion:", exc)
        pass

    if not el_time_picker_list is None:
        el_time_picker_list_size = len(el_time_picker_list)
        if show_debug_message:
            print("el_time_picker_list_size:", el_time_picker_list_size)

        if el_time_picker_list_size > 0:
            # default use main time.
            book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time)
            
            if show_debug_message:
                print("booking target time:", book_now_time)
                print("book_time_ret, book_fail_code:", book_time_ret, book_fail_code)
            
            if not book_time_ret:
                if book_fail_code >= 200:
                    # [200,201] ==> retry
                    # retry main target time.
                    book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time)
                    if show_debug_message:
                        print("retry booking target time:", book_time_ret, book_fail_code)
                else:
                    # try alt time.
                    book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time_alt)
                    if show_debug_message:
                        print("booking ALT time:", book_now_time_alt)
                        print("booking ALT target time:", book_time_ret, book_fail_code)
        else:
            if show_debug_message:
                print("time element length zero...")
    else:
        if show_debug_message:
            print("not found time elements.")

    
    return ret

def inline_reg(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False

    house_rules_ret = is_House_Rules_poped(driver)

    if show_debug_message:
        print("house_rules_ret:", house_rules_ret)

    if not house_rules_ret:
        adult_picker = config_dict["adult_picker"]
        force_adult_picker = config_dict["force_adult_picker"]

        # date picker.
        is_adult_picker_assigned = assign_adult_picker(driver, adult_picker, force_adult_picker)
        if show_debug_message:
            print("is_adult_picker_assigned:", is_adult_picker_assigned)

        if not is_adult_picker_assigned:
            # retry once.
            is_adult_picker_assigned = assign_adult_picker(driver, adult_picker, force_adult_picker)
            if show_debug_message:
                print("retry is_adult_picker_assigned:", is_adult_picker_assigned)

        # time picker.
        book_now_time = config_dict["book_now_time"]
        book_now_time_alt = config_dict["book_now_time_alt"]
        if is_adult_picker_assigned:
            ret = assign_time_picker(driver, book_now_time, book_now_time_alt)
            if show_debug_message:
                print("assign_time_picker return:", ret)

    return ret

def get_current_url(driver):
    DISCONNECTED_MSG = ': target window already closed'

    url = ""
    is_quit_bot = False

    try:
        url = driver.current_url
    except NoSuchWindowException:
        print('NoSuchWindowException at this url:', url )
        #print("last_url:", last_url)
        #print("get_log:", driver.get_log('driver'))
        window_handles_count = 0
        try:
            window_handles_count = len(driver.window_handles)
            #print("window_handles_count:", window_handles_count)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[0])
                driver.switch_to.default_content()
                time.sleep(0.2)
        except Exception as excSwithFail:
            #print("excSwithFail:", excSwithFail)
            pass
        if window_handles_count==0:
            try:
                driver_log = driver.get_log('driver')[-1]['message']
                print("get_log:", driver_log)
                if DISCONNECTED_MSG in driver_log:
                    print('quit bot by NoSuchWindowException')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()
            except Exception as excGetDriverMessageFail:
                #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                except_string = str(excGetDriverMessageFail)
                if 'HTTP method not allowed' in except_string:
                    print('quit bot by close browser')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

    except UnexpectedAlertPresentException as exc1:
        print('UnexpectedAlertPresentException at this url:', url )
        # PS: do nothing...
        # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
        # raise exception at selenium/webdriver/remote/errorhandler.py
        # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
        is_pass_alert = False
        is_pass_alert = True
        if is_pass_alert:
            try:
                driver.switch_to.alert.accept()
            except Exception as exc:
                pass

    except Exception as exc:
        logger.error('Maxbot URL Exception')
        logger.error(exc, exc_info=True)

        #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
        str_exc = ""
        try:
            str_exc = str(exc)
        except Exception as exc2:
            pass

        if len(str_exc)==0:
            str_exc = repr(exc)

        exit_bot_error_strings = ['Max retries exceeded'
        , 'chrome not reachable'
        , 'unable to connect to renderer'
        , 'failed to check if window was closed'
        , 'Failed to establish a new connection'
        , 'Connection refused'
        , 'disconnected'
        , 'without establishing a connection'
        , 'web view not found'
        , 'invalid session id'
        ]
        for each_error_string in exit_bot_error_strings:
            if isinstance(str_exc, str):
                if each_error_string in str_exc:
                    print('quit bot by error:', each_error_string)
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

        # not is above case, print exception.
        print("Exception:", str_exc)
        pass

    return url, is_quit_bot

def check_checkbox(driver, by, query):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    agree_checkbox = None
    try:
        agree_checkbox = driver.find_element(by, query)
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass
    is_checkbox_checked = False
    if agree_checkbox is not None:
        is_checkbox_checked = force_check_checkbox(driver, agree_checkbox)
    return is_checkbox_checked

def force_check_checkbox(driver, agree_checkbox):
    is_finish_checkbox_click = False
    if agree_checkbox is not None:
        is_visible = False
        try:
            if agree_checkbox.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            is_checkbox_checked = False
            try:
                if agree_checkbox.is_selected():
                    is_checkbox_checked = True
            except Exception as exc:
                pass

            if not is_checkbox_checked:
                #print('send check to checkbox')
                try:
                    agree_checkbox.click()
                    is_finish_checkbox_click = True
                except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", agree_checkbox)
                        is_finish_checkbox_click = True
                    except Exception as exc:
                        pass
            else:
                is_finish_checkbox_click = True
    return is_finish_checkbox_click

def force_press_button(driver, select_by, select_query, force_submit=True):
    is_clicked = False
    next_step_button = None
    try:
        next_step_button = driver.find_element(select_by ,select_query)
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                is_clicked = True
    except Exception as exc:
        #print("find %s clickable Exception:" % (select_query))
        #print(exc)
        pass

        if force_submit:
            if not next_step_button is None:
                is_visible = False
                try:
                    if next_step_button.is_enabled():
                        is_visible = True
                except Exception as exc:
                    pass

                if is_visible:
                    try:
                        driver.set_script_timeout(1)
                        driver.execute_script("arguments[0].click();", next_step_button)
                        is_clicked = True
                    except Exception as exc:
                        pass
    return is_clicked

def assign_select_by_text(driver, by, query, val):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_text_sent = False
    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        select_obj = None
        if el_text is not None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    select_obj = Select(el_text)
                    if not select_obj is None:
                        select_obj.select_by_visible_text(val)
                        is_text_sent = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass
            
    return is_text_sent

def assign_text(driver, by, query, val, overwrite = False, submit=False):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_visible = False

    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if el_text is not None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    is_visible = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

    is_text_sent = False
    if is_visible:
        try:
            inputed_text = el_text.get_attribute('value')
            if inputed_text is not None:
                is_do_keyin = False
                if len(inputed_text) == 0:
                    is_do_keyin = True
                else:
                    if inputed_text == val:
                        is_text_sent = True
                    else:
                        if overwrite:
                            el_text.clear()
                            is_do_keyin = True

                if is_do_keyin:
                    el_text.click()
                    el_text.send_keys(val)
                    if submit:
                        el_text.send_keys(Keys.ENTER)
                    is_text_sent = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass
            
    return is_text_sent

def inline_change_lang(driver, url):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    el_current_lang = None
    try:
        my_css_selector = "div.current"
        el_current_lang = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_current_lang is None:
            if el_current_lang.is_displayed():
                lang_name = el_current_lang.text
                #print("current language name:", lang_name)
                if len(lang_name) > 0:
                    if lang_name != "繁中":
                        new_url = url
                        if "?language=" in new_url:
                            new_url = new_url.split("?language=")[0]
                        new_url = new_url + "?language=zh-tw"
                        print("redirect to new zh-tw url:", new_url)
                        driver.get(new_url)
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

def main(args):
    config_dict = get_config_dict(args)

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict)
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    while True:
        time.sleep(0.05)

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        url, is_quit_bot = get_current_url(driver)
        try:
            if solve_press_and_hold_if_needed(driver):
                time.sleep(0.5)
        except Exception:
            pass
        if is_quit_bot:
            break

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        is_maxbot_paused = False
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            is_maxbot_paused = True

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                if is_maxbot_paused:
                    print("MAXBOT Paused.")
            last_url = url

        if is_maxbot_paused:
            time.sleep(0.2)
            continue

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url

        target_domain_list = ['//inline.app/booking/']
        for each_domain in target_domain_list:
            if each_domain in url:
                inline_change_lang(driver, url)
                current_progress_array = url.split('/')
                current_progress_length = len(current_progress_array)
                if current_progress_length >= 6:
                    branch_field = current_progress_array[5]
                    if len(branch_field) >= 0:
                        is_form_mode = False
                        if current_progress_length >= 7:
                            if current_progress_array[6] == 'form':
                                is_form_mode = True

                        if is_form_mode:
                            # fill personal info.
                            ret = fill_personal_info(driver, config_dict)
                        else:
                            # select date.
                            ret = inline_reg(driver, config_dict)


def cli():
    parser = argparse.ArgumentParser(
            description="MaxBot Aggument Parser")

    parser.add_argument("--input",
        help="config file path",
        type=str)

    parser.add_argument("--homepage",
        help="overwrite homepage setting",
        type=str)

    args = parser.parse_args()
    main(args)

if __name__ == "__main__":
    cli()
