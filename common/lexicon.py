import re
import yaml
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Pattern:
    regex: str
    label: str
    severity: str
    description: str
    template: str # [NEW]

@dataclass
class MatchResult:
    label: str
    severity: str
    formatted_message: Optional[str] = None
    leads: List[str] = None

class Lexicon:
    def __init__(self, system_name: str, definitions: List[dict]):
        self.system_name = system_name
        self.patterns: List[Pattern] = []
        for d in definitions:
            try:
                self.patterns.append(Pattern(
                    regex=d['regex'],
                    label=d['label'],
                    severity=d.get('severity', 'INFO'),
                    description=d.get('description', ''),
                    template=d.get('template', '{details}') # Default template
                ))
            except KeyError:
                pass

    def match(self, text: str) -> Optional[Tuple[Pattern, re.Match]]:
        for p in self.patterns:
            m = re.search(p.regex, text)
            if m:
                return p, m
        return None

class LexiconRegistry:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.lexicons: Dict[str, Lexicon] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.config_dir):
            return
        
        for f in os.listdir(self.config_dir):
            if f.endswith(".yaml"):
                system_name = f.replace(".yaml", "")
                try:
                    with open(os.path.join(self.config_dir, f), 'r') as fh:
                        data = yaml.safe_load(fh)
                        if isinstance(data, list):
                            self.lexicons[system_name] = Lexicon(system_name, data)
                except Exception:
                    pass

    def classify(self, system: str, text: str) -> MatchResult:
        """Returns MatchResult or MatchResult(label='NOISE')"""
        if system not in self.lexicons:
            return MatchResult(label="NOISE", severity="UNKNOWN")
        
        result = self.lexicons[system].match(text)
        if result:
            pattern, match_obj = result
            
            # Format logic
            try:
                # Support named groups: {port}
                # Support indexed groups: {0}, {1}
                # Support simple replacement of whole match if no groups
                
                groups = match_obj.groupdict()
                if not groups:
                    # Fallback to indexed groups
                    # We pass 'details' as the full match string for convenience
                    groups = {"details": match_obj.group(0)}
                    for i, g in enumerate(match_obj.groups()):
                        groups[str(i+1)] = g
                else:
                    groups["details"] = match_obj.group(0) # Ensure details exists

                formatted = pattern.template.format(**groups)
            except Exception:
                formatted = f"{pattern.label}: {text[:50]}..." # Fallback
                
            return MatchResult(
                label=pattern.label, 
                severity=pattern.severity, 
                formatted_message=formatted
            )
            
        return MatchResult(label="NOISE", severity="UNKNOWN")
