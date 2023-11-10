import { Streamlit, StreamlitComponentBase, withStreamlitConnection } from "streamlit-component-lib";
import React, { ReactNode } from "react";
import CSS from 'csstype';

interface State {
  selectedText: string;
  textColor: string;
  allSelectedWords: string[];
}


class SelectedTextDisplay extends StreamlitComponentBase<State> {
  public state = { selectedText: "", textColor: "#000000", allSelectedWords: ['']};

  public render = (): ReactNode => {
    var placeholder;
    const txt = this.props.args["txt"]
    const {textColor} = this.state;
    const words = txt.split(' ');
    const textWithSpans = words.map((word: string, index: number) => {
      const selected = this.state.selectedText;
      this.state.allSelectedWords.push(this.state.selectedText);
      const wordnopunc = word.replace(/[^\w\s']/g, '');
      const borderColor = this.state.allSelectedWords.includes(wordnopunc) ? "label label-warning" : "";   
      return (
        <span key={index} className={borderColor}>
          {word}{' '}
        </span>
      );
    });
    return (
      <div>
        <h3><p>{textWithSpans}</p></h3>
        <button onClick={this.displaySelectedText}>Select Text</button>
      </div>
    );
  };

  private getSelectedText = (): string => {
    const text = window.getSelection()?.toString() || "";
    return text;
  };

  private displaySelectedText = (): void => {
    const text = this.getSelectedText();
    this.setState(
      () => ({ selectedText: `${text}` }), 
      () => {
        const newColor = this.state.textColor  === "initial-color" ? "new-color" : "initial-color";
        this.setState({textColor: "#AA4A44"});
        Streamlit.setComponentValue(this.state.selectedText);
      }
    );
  };
}

export default withStreamlitConnection(SelectedTextDisplay)
