package com.multisensor.recording.ui.components

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.multisensor.recording.databinding.FragmentOnboardingPageBinding

class OnboardingPageFragment : Fragment() {

    private var _binding: FragmentOnboardingPageBinding? = null
    private val binding get() = _binding!!

    private var title: String? = null
    private var description: String? = null
    private var iconRes: Int = 0
    private var features: ArrayList<String>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            title = it.getString(ARG_TITLE)
            description = it.getString(ARG_DESCRIPTION)
            iconRes = it.getInt(ARG_ICON_RES)
            features = it.getStringArrayList(ARG_FEATURES)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentOnboardingPageBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.apply {
            titleText.text = title
            titleText.contentDescription = "Tutorial page title: $title"

            descriptionText.text = description
            descriptionText.contentDescription = "Tutorial description: $description"

            iconImage.setImageResource(iconRes)
            iconImage.contentDescription = "Tutorial page icon"

            features?.let { featureList ->
                featuresText.text = featureList.joinToString("\n\n")
                featuresText.contentDescription = "Features list: ${featureList.joinToString(", ")}"
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        private const val ARG_TITLE = "title"
        private const val ARG_DESCRIPTION = "description"
        private const val ARG_ICON_RES = "icon_res"
        private const val ARG_FEATURES = "features"

        fun newInstance(
            title: String,
            description: String,
            iconRes: Int,
            showFeatures: List<String>
        ): OnboardingPageFragment {
            return OnboardingPageFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_TITLE, title)
                    putString(ARG_DESCRIPTION, description)
                    putInt(ARG_ICON_RES, iconRes)
                    putStringArrayList(ARG_FEATURES, ArrayList(showFeatures))
                }
            }
        }
    }
}